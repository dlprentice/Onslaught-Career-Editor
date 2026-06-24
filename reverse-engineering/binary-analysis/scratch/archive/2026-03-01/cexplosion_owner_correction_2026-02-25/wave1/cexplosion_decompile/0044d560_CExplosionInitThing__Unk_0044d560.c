/* address: 0x0044d560 */
/* name: CExplosionInitThing__Unk_0044d560 */
/* signature: void __fastcall CExplosionInitThing__Unk_0044d560(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CExplosionInitThing__Unk_0044d560(int param_1)

{
  int iVar1;
  float fVar2;
  int local_8;

  if (*(int *)(param_1 + 0x1f8c) != 0) {
    iVar1 = *(int *)(param_1 + 0x1f80);
    if (iVar1 == 0) {
      fVar2 = _DAT_00679af8 * _DAT_005d85d0 + *(float *)(param_1 + 0x1f7c);
      *(float *)(param_1 + 0x1f7c) = fVar2;
      if (*(float *)(param_1 + 0x1f78) <= fVar2) {
        *(undefined4 *)(param_1 + 0x1f80) = 1;
      }
      local_8 = (int)(longlong)
                     ROUND((*(float *)(param_1 + 0x1f7c) / *(float *)(param_1 + 0x1f78)) *
                           _DAT_005d8c70);
      if (local_8 < 0) {
        *(undefined4 *)(param_1 + 0x18) = 0;
        return;
      }
      if (0xff < local_8) {
        local_8 = 0xff;
      }
    }
    else {
      if (iVar1 == 1) {
        if (*(int *)(param_1 + 0x1f90) == 0) {
          if ((*(int *)(param_1 + 0x1f98) == 0) &&
             (fVar2 = _DAT_00679af8 * _DAT_005d85d0 + *(float *)(param_1 + 0x1f88),
             *(float *)(param_1 + 0x1f88) = fVar2, *(float *)(param_1 + 0x1f84) <= fVar2)) {
            *(undefined4 *)(param_1 + 0x1f7c) = 0;
            *(undefined4 *)(param_1 + 0x1f80) = 2;
            *(undefined4 *)(param_1 + 0x1fa8) = 0xfffffffe;
          }
        }
        else if (_DAT_005d8568 <= *(float *)(param_1 + 0x1f94)) {
          *(undefined4 *)(param_1 + 0x1f80) = 2;
          *(undefined4 *)(param_1 + 0x18) = 0xff;
          return;
        }
        *(undefined4 *)(param_1 + 0x18) = 0xff;
        return;
      }
      if (iVar1 != 2) {
        return;
      }
      fVar2 = *(float *)(param_1 + 0x1f7c) + _DAT_005d8568;
      *(float *)(param_1 + 0x1f7c) = fVar2;
      if (*(float *)(param_1 + 0x1f78) <= fVar2) {
        *(undefined4 *)(param_1 + 0x1f80) = 0;
        *(undefined4 *)(param_1 + 0x1f8c) = 0;
        return;
      }
      local_8 = (int)(longlong)
                     ROUND((_DAT_005d8568 - fVar2 / *(float *)(param_1 + 0x1f78)) * _DAT_005d8c70);
      if (local_8 < 0) {
        *(undefined4 *)(param_1 + 0x18) = 0;
        return;
      }
      if (0xff < local_8) {
        *(undefined4 *)(param_1 + 0x18) = 0xff;
        return;
      }
    }
    *(int *)(param_1 + 0x18) = local_8;
  }
  return;
}
