<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format" xmlns:office="urn:oasis:names:tc:opendocument:xmlns:office:1.0" xmlns:text="urn:oasis:names:tc:opendocument:xmlns:text:1.0" xmlns:draw="urn:oasis:names:tc:opendocument:xmlns:drawing:1.0" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:svg="urn:oasis:names:tc:opendocument:xmlns:svg-compatible:1.0" >

  <xsl:template match="a">
    <xsl:choose>
      <xsl:when test="img">
        <xsl:apply-templates />
      </xsl:when>
      <xsl:otherwise>
        <xsl:text> </xsl:text>
        <xsl:value-of select="." />
        <text:note text:note-class="footnote" text:id="{generate-id()}">
          <text:note-citation><xsl:number count="a" format="1" /></text:note-citation>
          <text:note-body>
            <text:p text:style-name="Footnote">
              <xsl:value-of select="@href" />
            </text:p>
          </text:note-body>
        </text:note>
        <xsl:text> </xsl:text>
      </xsl:otherwise>
    </xsl:choose>
  </xsl:template>

</xsl:stylesheet>

