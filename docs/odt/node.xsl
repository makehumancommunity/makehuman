<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">

  <xsl:template match="node">
    <text:h text:style-name="Head2" text:outline-level="2">
      <xsl:number count="section|node" level="multiple" format="1.1. " /><xsl:value-of select="@title" /><xsl:text> (NID: </xsl:text><xsl:value-of select="@id" /><xsl:text>)</xsl:text>
    </text:h>
    <xsl:apply-templates />
  </xsl:template>

</xsl:stylesheet>

