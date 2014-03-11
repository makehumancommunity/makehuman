<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:fo="http://www.w3.org/1999/XSL/Format">

  <xsl:template match="a">

    <xsl:choose>
      <xsl:when test="img">
<xsl:text>

.. image:: </xsl:text><xsl:value-of select="@href" />

<xsl:text>

</xsl:text>
      </xsl:when>
      <xsl:otherwise><xsl:value-of select="." /> ( <xsl:value-of select="@href" />) </xsl:otherwise>
    </xsl:choose>

    </xsl:template>

</xsl:stylesheet>

