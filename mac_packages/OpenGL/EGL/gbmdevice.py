"""Utility module for interacting with GBM to select rendering device

The base code here comes from github bug report #6 in the pyopengl
project, thanks to @abandoned-cocoon for that.
"""
import weakref, ctypes, logging, os, glob
from OpenGL.platform import ctypesloader
from OpenGL import _opaque
log = logging.getLogger(__name__)
gbm = ctypesloader.loadLibrary(ctypes.CDLL,"gbm")
__all__ = ('enumerate_devices','open_device','close_device','gbm')
_DEVICE_HANDLES = {}
GBM_BO_USE_SCANOUT = (1 << 0)
GBM_BO_USE_CURSOR = (1 << 1)
GBM_BO_USE_CURSOR_64X64 = GBM_BO_USE_CURSOR
GBM_BO_USE_RENDERING = (1 << 2)
GBM_BO_USE_WRITE = (1 << 3)
GBM_BO_USE_LINEAR = (1 << 4)

GBMDevice = _opaque.opaque_pointer_cls('GBMDevice')
GBMSurface = _opaque.opaque_pointer_cls('GBMSurface')
gbm.gbm_create_device.restype = GBMDevice
gbm.gbm_surface_create.restype = GBMSurface

def filter_bad_drivers(cards, bad_drivers=('nvidia',)):
    """Lookup the driver for each card to exclude loading nvidia devices"""
    # this is pci specific, which I suppose means we're going to fail
    # if the GPU isn't on the PCI bus, but we don't seem to have
    # another way to match up the card to the driver :(
    bad_cards = set()
    for link in glob.glob('/dev/dri/by-path/pci-*-card'):
        base = os.path.basename(link)
        pci_id = base[4:-5]
        driver = os.path.basename(os.readlink('/sys/bus/pci/devices/%s/driver'%(pci_id,)))
        if driver in bad_drivers:
            card = os.path.basename(os.readlink(link))
            log.debug("Skipping %s because it uses %s driver",card,driver)
            bad_cards.add(card)
    filtered = [
        card for card in cards 
        if os.path.basename(card) not in bad_cards
    ]
    # assert len(filtered) == 1, filtered
    return filtered

def enumerate_devices():
    """Enumerate the set of gbm renderD* devices on the system
    
    Attempts to filter out any nvidia drivers with filter_bad_drivers
    along the way.
    """
    import glob
    # gbm says card* is the correct entry point...
    return filter_bad_drivers(sorted(glob.glob('/dev/dri/card*')))
def open_device(path):
    """Open a particular gbm device
    
    * path -- integer index of devices in sorted enumeration, or
              device basename (`renderD128`) or a full path-name
              as returned from enumerate_devices

    Will raise (at least):

    * RuntimeError for invalid indices
    * IOError/OSError for device access failures
    * RuntimeError if we cannot create the gbm device

    Caller is responsible for calling close_device(display) on the 
    resulting opaque pointer in order to release the open file-handle
    and deallocate the gbm_device record.

    returns GBMDevice, an opaque pointer
    """
    if isinstance(path,int):
        try:
            devices = enumerate_devices()
            path = devices[int]
        except IndexError:
            raise RuntimeError('Only %s devices available, cannot use 0-index %s'%(len(devices),path))
    else:
        path = os.path.join('/dev/dri',path) # allow for specifying "renderD128"
    log.debug("Final device path: %s", path)
    fh = open(path,'w')
    dev = gbm.gbm_create_device(fh.fileno())
    if dev == 0:
        fh.close()
        raise RuntimeError('Unable to create rendering device for: %s'%(path))
    _DEVICE_HANDLES[dev] = fh
    return dev
def close_device(device):
    """Close an opened gbm device"""
    gbm.gbm_device_destroy(device)
    try:
        handle = _DEVICE_HANDLES.pop(device)
        handle.close()
    except KeyError:
        pass

def create_surface(device, width=512, height=512, format=None, flags=GBM_BO_USE_RENDERING):
    """Create a GBM surface to use on the given device
    
    devices -- opaque GBMDevice pointer
    width,height -- dimensions
    format -- EGL_NATIVE_VISUAL_ID from an EGL configuration
    flags -- surface flags regarding reading/writing pattern that
             is expected for the buffer
    
    returns GBMSurface opaque pointer
    """
    if not format:
        raise ValueError(
            'Use eglGetConfigAttrib(display,config,EGL_NATIVE_VISUAL_ID) to get the native surface format',
        )
    return gbm.gbm_surface_create(device, width, height, format, flags)