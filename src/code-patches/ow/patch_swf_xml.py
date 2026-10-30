import re,html
src='/root/work/ffdec/fe.xml'; dst='/root/work/ow/fe_ow.xml'
x=open(src,encoding='utf-8').read()
SHAPE_ID,TEXT_ID=1400,1401
O=2856+4*2900          # slot 5 (after Call of the Dead)
W,Y0,H=2660,31,3680
shape=f'''<item type="DefineShapeTag" forceWriteAsLong="true" shapeId="{SHAPE_ID}">
      <shapeBounds type="RECT" Xmax="{W}" Xmin="0" Ymax="{Y0+H}" Ymin="{Y0}" nbits="14"/>
      <shapes type="SHAPEWITHSTYLE" numFillBits="2" numLineBits="0">
        <fillStyles type="FILLSTYLEARRAY">
          <fillStyles>
            <item type="FILLSTYLE" bitmapId="65535" fillStyleType="65">
              <bitmapMatrix type="MATRIX" hasRotate="false" hasScale="true" nRotateBits="0" nScaleBits="22" nTranslateBits="0" rotateSkew0="0.0" rotateSkew1="0.0" scaleX="20.0" scaleY="20.0" translateX="0" translateY="0"/>
            </item>
            <item type="FILLSTYLE" bitmapId="984" fillStyleType="65">
              <bitmapMatrix type="MATRIX" hasRotate="false" hasScale="true" nRotateBits="0" nScaleBits="22" nTranslateBits="7" rotateSkew0="0.0" rotateSkew1="0.0" scaleX="20.0" scaleY="20.0" translateX="0" translateY="{Y0}"/>
            </item>
          </fillStyles>
        </fillStyles>
        <lineStyles type="LINESTYLEARRAY">
          <lineStyles/>
          <lineStyles2/>
        </lineStyles>
        <shapeRecords>
          <item type="StyleChangeRecord" fillStyle0="0" fillStyle1="2" lineStyle="0" moveBits="14" moveDeltaX="{W}" moveDeltaY="{Y0+H}" numFillBits="0" numLineBits="0" stateFillStyle0="false" stateFillStyle1="true" stateLineStyle="false" stateMoveTo="true" stateNewStyles="false"/>
          <item type="StraightEdgeRecord" deltaX="-{W}" deltaY="0" generalLineFlag="false" numBits="12" vertLineFlag="false"/>
          <item type="StraightEdgeRecord" deltaX="0" deltaY="-{H}" generalLineFlag="false" numBits="12" vertLineFlag="true"/>
          <item type="StraightEdgeRecord" deltaX="{W}" deltaY="0" generalLineFlag="false" numBits="12" vertLineFlag="false"/>
          <item type="StraightEdgeRecord" deltaX="0" deltaY="{H}" generalLineFlag="false" numBits="12" vertLineFlag="true"/>
          <item type="EndShapeRecord" endOfShape="0"/>
        </shapeRecords>
      </shapes>
    </item>
    '''
label_html='<p align="center"><font face="CCAdamKubert" size="19" color="#ffffff" letterSpacing="-2.000000" kerning="1"><b><i>One Window</i></b></font></p>'
m=re.search(r'<item type="DefineEditTextTag"[^>]*characterID="990"[^>]*>.*?</item>',x,re.S)
t=m.group(0)
t=t.replace('characterID="990"',f'characterID="{TEXT_ID}"')
t=re.sub(r'initialText="[^"]*"','initialText="%s"'%html.escape(label_html,quote=True),t)
t=re.sub(r'<bounds [^>]*/>','<bounds type="RECT" Xmax="3592" Xmin="-40" Ymax="899" Ymin="-40" nbits="13"/>',t)
text=t+'\n    '
sp=re.search(r'<item type="DefineSpriteTag"[^>]*spriteId="996"',x)
assert sp
x=x[:sp.start()]+shape+text+x[sp.start():]
sp=re.search(r'<item type="DefineSpriteTag"[^>]*spriteId="996"',x)
end=x.find('</subTags>',sp.start())
show=x.rfind('<item type="ShowFrameTag"',sp.start(),end)
place=f'''<item type="PlaceObject2Tag" characterId="{SHAPE_ID}" clipDepth="0" depth="11" forceWriteAsLong="true" name="onewindow_card" placeFlagHasCharacter="true" placeFlagHasClipActions="false" placeFlagHasClipDepth="false" placeFlagHasColorTransform="true" placeFlagHasMatrix="true" placeFlagHasName="true" placeFlagHasRatio="false" placeFlagMove="false" ratio="0">
          <matrix type="MATRIX" hasRotate="false" hasScale="false" nRotateBits="0" nScaleBits="0" nTranslateBits="17" rotateSkew0="0.0" rotateSkew1="0.0" scaleX="0.0" scaleY="0.0" translateX="{O}" translateY="0"/>
          <colorTransform type="CXFORMWITHALPHA" alphaAddTerm="0" alphaMultTerm="256" blueAddTerm="0" blueMultTerm="170" greenAddTerm="0" greenMultTerm="170" hasAddTerms="false" hasMultTerms="true" nbits="10" redAddTerm="0" redMultTerm="256"/>
        </item>
        <item type="PlaceObject2Tag" characterId="{TEXT_ID}" clipDepth="0" depth="12" forceWriteAsLong="true" name="onewindow" placeFlagHasCharacter="true" placeFlagHasClipActions="false" placeFlagHasClipDepth="false" placeFlagHasColorTransform="false" placeFlagHasMatrix="true" placeFlagHasName="true" placeFlagHasRatio="false" placeFlagMove="false" ratio="0">
          <matrix type="MATRIX" hasRotate="true" hasScale="true" nRotateBits="13" nScaleBits="17" nTranslateBits="17" rotateSkew0="-0.03489685" rotateSkew1="0.03489685" scaleX="0.99938965" scaleY="0.99938965" translateX="{O-460}" translateY="2823"/>
        </item>
        '''
x=x[:show]+place+x[show:]
open(dst,'w',encoding='utf-8').write(x)
print('ok')
