/* address: 0x00459e50 */
/* name: CFEPMultiplayerStart__SubObj8848__RenderPreCommon */
/* signature: undefined CFEPMultiplayerStart__SubObj8848__RenderPreCommon(void) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFEPMultiplayerStart__SubObj8848__RenderPreCommon(float param_1)

{
  float fVar1;
  float fVar2;
  int iStack_8;

  if (_DAT_005d85ec < param_1) {
    fVar1 = (param_1 - _DAT_005d8bc4) * _DAT_005d85bc;
    fVar2 = _DAT_005d856c;
    if ((_DAT_005d856c <= fVar1) && (fVar2 = fVar1, _DAT_005d8568 < fVar1)) {
      fVar2 = _DAT_005d8568;
    }
    iStack_8 = (int)(longlong)ROUND(fVar2 * _DAT_005d8c70);
    CUnitAI__Unk_00452ce0(1.0,iStack_8 * 0x3f0000 | 0xffffff,-9999999.0,-9999999.0);
  }
  return;
}
