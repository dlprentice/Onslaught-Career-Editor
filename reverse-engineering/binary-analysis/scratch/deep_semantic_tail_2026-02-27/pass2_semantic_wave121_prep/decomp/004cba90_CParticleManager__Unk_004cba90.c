/* address: 0x004cba90 */
/* name: CParticleManager__Unk_004cba90 */
/* signature: double __stdcall CParticleManager__Unk_004cba90(int param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double CParticleManager__Unk_004cba90(int param_1)

{
  float *pfVar1;
  float fVar2;
  int iVar3;
  undefined4 *puVar4;
  int unaff_retaddr;
  float local_24;
  float local_20;
  float local_1c;
  float local_18;
  float local_14;
  float local_10;
  float fStack_c;
  float fStack_8;

  iVar3 = CExplosionInitThing__Helper_004725d0(0x8a9a98);
  if (iVar3 != 0) {
    local_24 = 1e+07;
    pfVar1 = *(float **)(param_1 + 0x58);
    local_20 = *(float *)(param_1 + 0x38);
    local_1c = *(float *)(param_1 + 0x3c);
    local_18 = *(float *)(param_1 + 0x40);
    if (pfVar1 != (float *)0x0) {
      local_20 = local_20 + *pfVar1;
      local_1c = local_1c + pfVar1[1];
      local_18 = local_18 + pfVar1[2];
    }
    puVar4 = CGame__GetCamera(&DAT_008a9a98,0);
    if (puVar4 != (undefined4 *)0x0) {
      (**(code **)*puVar4)(&local_10);
      fVar2 = (local_10 - local_20) * (local_10 - local_20) +
              (fStack_c - local_1c) * (fStack_c - local_1c) +
              (fStack_8 - local_18) * (fStack_8 - local_18);
      if (fVar2 < _DAT_005ddbb0) {
        local_24 = fVar2;
      }
    }
    puVar4 = CGame__GetCamera(&DAT_008a9a98,1);
    if (puVar4 != (undefined4 *)0x0) {
      (**(code **)*puVar4)(&local_10);
      fVar2 = (local_10 - local_20) * (local_10 - local_20) +
              (fStack_c - local_1c) * (fStack_c - local_1c) +
              (fStack_8 - local_18) * (fStack_8 - local_18);
      if (fVar2 < local_24) {
        return (double)fVar2;
      }
    }
    return (double)local_24;
  }
  if ((undefined4 *)(&DAT_0089c9a4)[DAT_0089ce4c] == (undefined4 *)0x0) {
    return (double)_DAT_005d856c;
  }
  (*(code *)**(undefined4 **)(&DAT_0089c9a4)[DAT_0089ce4c])(&local_10);
  pfVar1 = *(float **)(unaff_retaddr + 0x58);
  fVar2 = *(float *)(unaff_retaddr + 0x38);
  local_20 = *(float *)(unaff_retaddr + 0x3c);
  local_1c = *(float *)(unaff_retaddr + 0x40);
  if (pfVar1 != (float *)0x0) {
    fVar2 = fVar2 + *pfVar1;
    local_20 = local_20 + pfVar1[1];
    local_1c = local_1c + pfVar1[2];
  }
  return (double)((local_14 - fVar2) * (local_14 - fVar2) +
                 (local_10 - local_20) * (local_10 - local_20) +
                 (fStack_c - local_1c) * (fStack_c - local_1c));
}
