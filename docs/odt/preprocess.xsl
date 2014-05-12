<?xml version="1.0" encoding="utf-8" ?>
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform"> 

  <xsl:param name="volume" select="'User guide'"/>

  <xsl:strip-space elements="li"/>
  <xsl:preserve-space elements="pre"/>

  <xsl:key name="sectionids" match="node" use="Sid" />

  <xsl:template match="nodes">

<document>
      <xsl:text>
</xsl:text>
    <xsl:for-each select="node[count(. | key('sectionids', Sid)[1]) = 1]">      
      <xsl:sort data-type="number" select="sectionweight"/>
      <xsl:if test="Volume=$volume">
      <xsl:variable name="sectid" select="Sid" />
      <section>
      <xsl:attribute name="id">
        <xsl:value-of select="Sid" />
      </xsl:attribute>
      <xsl:attribute name="volume">
        <xsl:value-of select="Volume" />
      </xsl:attribute>
      <xsl:attribute name="weight">
        <xsl:value-of select="sectionweight" />
      </xsl:attribute>
      <xsl:attribute name="title">
        <xsl:value-of select="Section" />
      </xsl:attribute>
        <xsl:text>
</xsl:text>
      <xsl:copy-of select="sectionbody" />
      <xsl:for-each select="../node[Sid=$sectid]">
        <node>
        <xsl:attribute name="weight">
          <xsl:value-of select="weight" />
        </xsl:attribute>
        <xsl:attribute name="title">
          <xsl:value-of select="title" />
        </xsl:attribute>
        <xsl:attribute name="id">
          <xsl:value-of select="Nid" />
        </xsl:attribute>
        <xsl:copy-of select="Body/node()" />
        </node>
        <xsl:text>
</xsl:text>

      </xsl:for-each>
      </section>
      <xsl:text>
</xsl:text>

      </xsl:if>
    </xsl:for-each>

</document>

  </xsl:template>

</xsl:stylesheet>

