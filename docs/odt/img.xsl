<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" >

  <xsl:template match="img">
    <xsl:variable name="imgsrc" select="@src" />
    <draw:frame draw:style-name="PastedImage" draw:name="{generate-id()}" text:anchor-type="paragraph" draw:z-index="0">
      <xsl:attribute name="svg:width">
        <xsl:value-of select="(//image[@file=$imgsrc])[1]/@width" />
      </xsl:attribute>
      <xsl:attribute name="svg:height">
        <xsl:value-of select="(//image[@file=$imgsrc])[1]/@height" />
      </xsl:attribute>
      <draw:image xlink:type="simple" xlink:show="embed" xlink:actuate="onLoad">
      <xsl:attribute name="xlink:href">
        <xsl:value-of select="@src" />
      </xsl:attribute>
      </draw:image>
    </draw:frame>
  </xsl:template>

</xsl:stylesheet>

