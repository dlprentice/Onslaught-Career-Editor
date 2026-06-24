/* address: 0x00453140 */
/* name: CFEPMultiplayerStart__Helper_00453140 */
/* signature: void __stdcall CFEPMultiplayerStart__Helper_00453140(float param_1, float param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFEPMultiplayerStart__Helper_00453140(float param_1,float param_2)

{
  float fVar1;
  bool bVar2;
  float fVar3;
  wchar_t *text;
  int iVar4;
  void *pvVar5;
  uint uVar6;
  int *out_extent_xy;
  int local_10;
  int local_c;
  longlong local_8;

  if (DAT_0089be58 != 0) {
    return;
  }
  if ((DAT_0089be64 != 0) && (DAT_0089d950 == 0xf)) {
    return;
  }
  bVar2 = false;
  text = Text__AsciiToWideScratch(s_Unknown_Help_String_00629098);
  switch(param_1) {
  case 0.0:
    text = Localization__GetStringById(0x2b);
    goto LAB_004531ef;
  case 1.4013e-45:
    text = Localization__GetStringById(0x2c);
    break;
  case 2.8026e-45:
    text = Localization__GetStringById(0x2d);
    break;
  case 4.2039e-45:
  case 8.40779e-45:
    text = Localization__GetStringById(0x30);
  default:
    if (((int)param_1 < 1) || ((3 < (int)param_1 && (param_1 != 8.40779e-45)))) goto LAB_004531ef;
    break;
  case 5.60519e-45:
    text = Localization__GetStringById(0x2e);
    goto LAB_004531ef;
  case 7.00649e-45:
    text = Localization__GetStringById(0x2f);
    goto LAB_004531ef;
  }
  bVar2 = true;
LAB_004531ef:
  iVar4 = CFrontEnd__IsMouseInputReady(0x675688);
  if (iVar4 == 0) {
    out_extent_xy = &local_10;
    fVar1 = (_DAT_005d8568 - param_2) * (_DAT_005d8568 - param_2) * _DAT_005db3fc;
    pvVar5 = CPlatform__Font(&DAT_0088a0a8,1);
    CDXFont__GetTextExtent(pvVar5,text,out_extent_xy);
    if (bVar2) {
      fVar3 = _DAT_005d8be8 - fVar1;
    }
    else {
      fVar3 = (_DAT_005db3f8 - (float)local_10) + fVar1;
    }
    CFrontEnd__GetCursorStateInRect
              ((int)fVar3,0x43e38000,(int)((float)local_10 + fVar3),
               (int)((float)local_c + _DAT_005db3f4));
    if (bVar2) {
      param_1 = fVar3 + _DAT_005d8bc0;
      param_2 = 3.1415927;
      pvVar5 = (void *)0x2e;
    }
    else {
      param_1 = fVar1 + _DAT_005db3f0;
      param_2 = 0.0;
      pvVar5 = (void *)0x2c;
    }
    local_8 = (longlong)ROUND(_DAT_008a9570);
    uVar6 = (uint)local_8 & 0x8000003f;
    if ((int)uVar6 < 0) {
      uVar6 = (uVar6 - 1 | 0xffffffc0) + 1;
    }
    if ((int)uVar6 < 0x32) {
      CDXSurf__RenderSurface
                (param_1,0x43e38000,0x3dcccccd,DAT_0089d840,0xffffffff,0x3f800000,0x3f800000,4,0,
                 0x3f800000,param_2);
    }
    CFrontEnd__ProcessMouseReadyOrDispatchVBufTexture
              ((void *)(param_1 - _DAT_005d8610),(void *)0x43cf8000,
               (void *)(param_1 + _DAT_005d8610),(void *)0x43f78000,pvVar5);
  }
  return;
}
