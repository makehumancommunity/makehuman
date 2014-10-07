<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">

  <xsl:template match="document">
<office:document-content xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:style="urn:oasis:names:tc:opendocument:xmlns:style:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:table="urn:oasis:names:tc:opendocument:xmlns:table:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:fo="urn:oasis:names:tc:opendocument:xmlns:xsl-fo-compatible:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:meta="urn:oasis:names:tc:opendocument:xmlns:meta:1.0" xmlns:number="urn:oasis:names:tc:opendocument:xmlns:datastyle:1.0" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" xmlns:chart="urn:oasis:names:tc:opendocument:xmlns:chart:1.0" xmlns:dr3d="urn:oasis:names:tc:opendocument:xmlns:dr3d:1.0" xmlns:math="http://www.w3.org/1998/Math/MathML" xmlns:form="urn:oasis:names:tc:opendocument:xmlns:form:1.0" xmlns:script="urn:oasis:names:tc:opendocument:xmlns:script:1.0" xmlns:ooo="http://openoffice.org/2004/office" xmlns:ooow="http://openoffice.org/2004/writer" xmlns:oooc="http://openoffice.org/2004/calc" xmlns:dom="http://www.w3.org/2001/xml-events" xmlns:xforms="http://www.w3.org/2002/xforms" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:rpt="http://openoffice.org/2005/report" xmlns:of="urn:oasis:names:tc:opendocument:xmlns:of:1.2" xmlns:xhtml="http://www.w3.org/1999/xhtml" xmlns:grddl="http://www.w3.org/2003/g/data-view#" xmlns:tableooo="http://openoffice.org/2009/table" xmlns:field="urn:openoffice:names:experimental:ooo-ms-interop:xmlns:field:1.0" xmlns:formx="urn:openoffice:names:experimental:ooxml-odf-interop:xmlns:form:1.0" xmlns:css3t="http://www.w3.org/TR/css3-text/" office:version="1.2">
  <office:scripts/>
  <office:font-face-decls>    
    <style:font-face style:name="Liberation Sans" svg:font-family="'Liberation Sans'" style:font-family-generic="swiss" style:font-pitch="variable"/>    
  </office:font-face-decls>
  <office:automatic-styles>
    <style:style style:name="PastedImage" style:family="graphic" style:parent-style-name="Graphics">
      <style:graphic-properties 
        style:run-through="foreground" 
        style:wrap="none" 
        style:horizontal-pos="center" 
        style:horizontal-rel="paragraph" 
        style:mirror="none" 
        fo:clip="rect(0cm, 0cm, 0cm, 0cm)" 
        draw:luminance="0%" draw:contrast="0%" 
        draw:red="0%" 
        draw:green="0%" 
        draw:blue="0%" 
        draw:gamma="100%" 
        draw:color-inversion="false" 
        draw:image-opacity="100%" 
        draw:color-mode="standard"/>
    </style:style>
    <style:style style:name="Warning" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0.423cm" fo:margin-bottom="0.212cm" fo:background-color="#ffffff" fo:keep-with-next="always">
        <style:background-image/>
      </style:paragraph-properties>
      <style:text-properties style:font-name="Liberation Sans" fo:font-size="14pt" fo:background-color="#ffff00"/>
    </style:style>
    <style:style style:name="Unimplemented" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0.423cm" fo:margin-bottom="0.212cm" fo:background-color="#ffffff" fo:keep-with-next="always">
        <style:background-image/>
      </style:paragraph-properties>
      <style:text-properties style:font-name="Liberation Sans" fo:font-size="14pt" fo:background-color="#66ccdd"/>
    </style:style>
    <style:style style:name="Link" style:family="paragraph" style:parent-style-name="Standard">
      <style:paragraph-properties fo:margin-top="0.423cm" fo:margin-bottom="0.212cm" fo:background-color="#ffffff" fo:keep-with-next="always">
        <style:background-image/>
      </style:paragraph-properties>
      <style:text-properties style:font-name="Liberation Sans" fo:color="#0000dd"/>
    </style:style>
    <style:style style:name="T1" style:family="text"> 
      <style:text-properties fo:color="#0000ff" />
    </style:style>
    <style:style style:name="STRONG" style:family="text"> 
      <style:text-properties fo:font-weight="bold" fo:color="#ff0000" />
    </style:style>
    <style:style style:name="EM" style:family="text"> 
      <style:text-properties fo:font-style="italic" fo:color="#00ff00" />
    </style:style>
    <text:list-style style:name="NumberedList">
        <text:list-level-style-number text:level="1"
            text:style-name="Numbering_20_Symbols"
            style:num-prefix=" " style:num-suffix="."
            style:num-format="1">
            <style:list-level-properties
                text:space-before="0.5cm"
                text:min-label-width="0.25in"/>
        </text:list-level-style-number>
    </text:list-style>
    <text:list-style style:name="UnorderedList">
        <text:list-level-style-bullet text:level="1"
            text:style-name="Bullet_20_Symbols"
            style:num-prefix=" " style:num-suffix=" "
            text:bullet-char="•">
            <style:list-level-properties
                text:space-before="0.5cm"
                text:min-label-width="0.25in"/>
            <style:text-properties style:font-name="StarSymbol"/>
        </text:list-level-style-bullet>
    </text:list-style>
  </office:automatic-styles>
  <office:body>
    <office:text>
      <text:sequence-decls>
        <text:sequence-decl text:display-outline-level="0" text:name="Illustration"/>
        <text:sequence-decl text:display-outline-level="0" text:name="Table"/>
        <text:sequence-decl text:display-outline-level="0" text:name="Text"/>
        <text:sequence-decl text:display-outline-level="0" text:name="Drawing"/>
      </text:sequence-decls>
      <text:p text:style-name="Warning">Insert title and front page graphics here</text:p>
      <xsl:apply-templates />
    </office:text>
  </office:body>
</office:document-content>
  </xsl:template>

</xsl:stylesheet>

