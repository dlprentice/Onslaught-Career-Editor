/* address: 0x0053bb50 */
/* name: CDXEngine__Helper_0053bb50 */
/* signature: void __fastcall CDXEngine__Helper_0053bb50(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CDXEngine__Helper_0053bb50(int param_1)

{
  undefined4 uVar1;
  bool bVar2;
  float10 fVar3;
  undefined4 uStack_8;

  if (*(int *)(param_1 + 300) != 0) {
    bVar2 = (_DAT_0089ce54 & 4) != 0;
    if (bVar2) {
      _DAT_0089ce54 = _DAT_0089ce54 & 0xfffffffb;
    }
    RenderState_Set(0x8f,1);
    if (*(int *)(param_1 + 0x8c) != 0) {
      uVar1 = 0;
      fVar3 = (float10)(**(code **)(**(int **)(param_1 + 0x110) + 0x16c))();
      if ((float10)_DAT_005d85d8 < fVar3) {
        fVar3 = (float10)(**(code **)(**(int **)(param_1 + 0x110) + 0x16c))();
        uVar1 = 0x40;
        uStack_8 = (undefined4)
                   (longlong)ROUND((float10)_DAT_005d8c70 - fVar3 * (float10)_DAT_005d8c74);
        DAT_0063012c = uStack_8;
      }
      (**(code **)(**(int **)(param_1 + 0x8c) + 8))(uVar1);
      DAT_0063012c = 0xff;
    }
    RenderState_Set(0x8f,0);
    if (bVar2) {
      if ((_DAT_0089ce54 & 4) != 0) {
        _DAT_0089ce54 = _DAT_0089ce54 & 0xfffffffb;
        return;
      }
      _DAT_0089ce54 = _DAT_0089ce54 | 4;
    }
  }
  return;
}
