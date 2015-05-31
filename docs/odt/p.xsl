<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">

  <xsl:template match="p">
    <xsl:for-each select="div">
      <xsl:apply-templates />
    </xsl:for-each>
    <xsl:for-each select="span">
      <xsl:apply-templates />
    </xsl:for-each>
    <text:p text:style-name="para">
      <xsl:apply-templates />
    </text:p>
  </xsl:template>

</xsl:stylesheet>

