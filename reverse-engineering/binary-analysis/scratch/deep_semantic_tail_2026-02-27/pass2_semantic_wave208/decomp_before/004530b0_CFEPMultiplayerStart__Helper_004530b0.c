/* address: 0x004530b0 */
/* name: CFEPMultiplayerStart__Helper_004530b0 */
/* signature: void __stdcall CFEPMultiplayerStart__Helper_004530b0(float param_1, float param_2, float param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFEPMultiplayerStart__Helper_004530b0(float param_1,float param_2,float param_3,int param_4)

{
  float fVar1;

  fVar1 = param_2 * param_3;
  if (DAT_006777c4 == 0) {
    param_2 = _DAT_005db3e8 - param_1 * param_3;
  }
  else {
    param_2 = 300.0;
  }
  CDXSurf__RenderSurface
            (param_2,_DAT_005db3ec - fVar1,0x3f747ae1,DAT_0089d838,
             (param_4 * 0xff & 0xffbfU) << 0x10 | 0xbfbfff,param_3,param_3,4,0,0x3f800000,0);
  return;
}
