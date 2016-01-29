<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">

  <xsl:template match="h2">
    <text:h text:style-name="Head3" text:outline-level="3">
      <xsl:number count="section|node|h2" level="multiple" format="1.1.1. " /><xsl:value-of select="." />
    </text:h>
  </xsl:template>

</xsl:stylesheet>

