/* address: 0x00450460 */
/* name: CFEPMultiplayerStart__Helper_00450460 */
/* signature: void __cdecl CFEPMultiplayerStart__Helper_00450460(float param_1, float param_2, float param_3, uint param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __cdecl
CFEPMultiplayerStart__Helper_00450460(float param_1,float param_2,float param_3,uint param_4)

{
  float fVar1;
  uint uVar2;
  int local_8;

  local_8 = (int)(longlong)ROUND(param_3 * _DAT_005db338);
  uVar2 = param_4 >> 0x18;
  param_1 = param_1 - (float)(local_8 + -1) * _DAT_005d8be8 * _DAT_005d85ec;
  switch(local_8 + -1) {
  case 0:
    param_4 = 0xffff6f4f;
    break;
  case 1:
  case 2:
    param_4 = 0xff4f6fff;
    break;
  case 3:
  case 4:
    param_4 = 0xff6fff5f;
  }
  if (0 < local_8) {
    fVar1 = param_2 + _DAT_005d8ba0;
    do {
      CDXSurf__RenderSurface
                (param_1 + _DAT_005d8ba0,fVar1,0x3dcccccd,DAT_0089d8e8,
                 (uVar2 * 0x7f & 0xff00) << 0x10,0x3f333333,0x3f333333,4,0,0x3f800000,0);
      CDXSurf__RenderSurface
                (param_1,param_2,0x3dcccccd,DAT_0089d8e8,
                 ((param_4 >> 8 & 0xffff0000) * uVar2 ^ param_4) & 0xffffff ^
                 (param_4 >> 8 & 0xff0000) * uVar2,0x3f333333,0x3f333333,4,0,0x3f800000,0);
      param_1 = param_1 + _DAT_005d8be8;
      local_8 = local_8 + -1;
    } while (local_8 != 0);
  }
  return;
}
