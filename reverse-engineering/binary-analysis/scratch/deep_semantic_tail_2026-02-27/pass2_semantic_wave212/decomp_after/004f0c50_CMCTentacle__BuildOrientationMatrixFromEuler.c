/* address: 0x004f0c50 */
/* name: CMCTentacle__BuildOrientationMatrixFromEuler */
/* signature: void __thiscall CMCTentacle__BuildOrientationMatrixFromEuler(void * this, int param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CMCTentacle__BuildOrientationMatrixFromEuler(void *this,int param_1,void *param_2)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  void *this_00;
  undefined4 *extraout_EAX;
  int iVar5;
  undefined4 *puVar6;
  void *unaff_EDI;
  float10 fVar7;
  float10 fVar8;
  undefined1 *puVar9;
  float *pfVar10;
  float local_c0;
  float local_bc;
  float local_b8;
  float local_b0;
  float local_ac;
  float local_a8;
  float local_a0;
  float local_9c;
  float local_98;
  undefined1 local_90 [48];
  undefined1 local_60 [48];
  undefined1 local_30 [48];

  fVar7 = (float10)fcos((float10)_DAT_005df4c8);
  fVar1 = (float)fVar7;
  fVar8 = (float10)fsin((float10)_DAT_005df4c8);
  local_9c = (float)fVar8;
  fVar2 = (float)fVar8;
  fVar8 = (float10)fcos((float10)_DAT_005d87b0);
  fVar3 = (float)fVar8;
  fVar8 = (float10)fsin((float10)_DAT_005d87b0);
  fVar4 = (float)fVar8;
  local_c0 = fVar3 * fVar1 - local_9c * fVar4 * fVar2;
  local_bc = (float)-(fVar7 * (float10)fVar2);
  local_b8 = fVar4 * fVar1 + local_9c * fVar3 * fVar2;
  local_b0 = fVar3 * fVar2 + local_9c * fVar4 * fVar1;
  local_ac = (float)(fVar7 * (float10)fVar1);
  local_a8 = fVar4 * fVar2 - local_9c * fVar3 * fVar1;
  local_a0 = (float)-(fVar7 * (float10)fVar4);
  local_98 = (float)(fVar7 * (float10)fVar3);
  CSquadNormal__BuildOrientationMatrixFromEuler
            (local_90,*(void **)((int)this + 0x2c4),*(float *)((int)this + 0x2c8) - _DAT_005d85e4,
             0.0,(float)unaff_EDI);
  pfVar10 = &local_c0;
  puVar9 = local_60;
  CMCBuggy__Helper_0040d320((void *)((int)this + 0x3c),local_30,local_90,puVar9);
  CMCBuggy__Helper_0040d320(this_00,puVar9,pfVar10,unaff_EDI);
  puVar6 = extraout_EAX;
  for (iVar5 = 0xc; iVar5 != 0; iVar5 = iVar5 + -1) {
    *(undefined4 *)param_1 = *puVar6;
    puVar6 = puVar6 + 1;
    param_1 = (int)(param_1 + 4);
  }
  return;
}
