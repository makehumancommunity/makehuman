<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0">

  <xsl:template match="div">
    <text:p text:style-name="Warning">
      DIV TAG! Contents ignored.
    </text:p>
  </xsl:template>

  <xsl:template match="DIV">
    <text:p text:style-name="Warning">
      DIV TAG! Contents ignored.
    </text:p>
  </xsl:template>


</xsl:stylesheet>

