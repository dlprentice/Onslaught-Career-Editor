/* address: 0x004c0150 */
/* name: CUnitAI__ComposeTransformFromOffset */
/* signature: void __stdcall CUnitAI__ComposeTransformFromOffset(int param_1, void * param_2, int param_3) */


void CUnitAI__ComposeTransformFromOffset(int param_1,void *param_2,int param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  undefined4 *extraout_EAX;
  int iVar10;
  undefined4 *puVar11;
  void *unaff_EDI;
  undefined4 *puVar12;
  undefined4 local_54;
  undefined1 local_40 [16];
  undefined4 local_30 [12];

  if (param_3 != 0) {
    *(void **)(param_1 + 0x58) = param_2;
    return;
  }
  if (param_2 != (void *)0x0) {
    if (*(int *)((int)param_2 + 0xa0) != 0) {
      fVar1 = *(float *)((int)param_2 + 0x20);
      fVar2 = *(float *)(param_1 + 0x38);
      fVar3 = *(float *)((int)param_2 + 0x28);
      fVar4 = *(float *)((int)param_2 + 0x24);
      fVar5 = *(float *)((int)param_2 + 0x30);
      fVar6 = *(float *)(param_1 + 0x38);
      fVar7 = *(float *)((int)param_2 + 0x38);
      fVar8 = *(float *)((int)param_2 + 0x34);
      fVar9 = *(float *)(param_1 + 0x3c);
      *(float *)(param_1 + 0x38) =
           *(float *)(param_1 + 0x38) * *(float *)((int)param_2 + 0x10) +
           *(float *)((int)param_2 + 0x14) * *(float *)(param_1 + 0x3c) +
           *(float *)((int)param_2 + 0x18) * *(float *)(param_1 + 0x40);
      *(float *)(param_1 + 0x3c) =
           fVar4 * *(float *)(param_1 + 0x3c) + fVar3 * *(float *)(param_1 + 0x40) + fVar1 * fVar2;
      *(float *)(param_1 + 0x40) =
           fVar8 * fVar9 + fVar7 * *(float *)(param_1 + 0x40) + fVar5 * fVar6;
      *(undefined4 *)(param_1 + 0x44) = local_54;
      Vec3__SetXYZ();
      Vec3__SetXYZ();
      Vec3__SetXYZ();
      Mat34__SetRows();
      puVar11 = local_30;
      puVar12 = (undefined4 *)(param_1 + 8);
      for (iVar10 = 0xc; iVar10 != 0; iVar10 = iVar10 + -1) {
        *puVar12 = *puVar11;
        puVar11 = puVar11 + 1;
        puVar12 = puVar12 + 1;
      }
      CSquadNormal__Helper_0040d2c0
                ((float *)((int)param_2 + 0x10),local_40,(undefined4 *)(param_1 + 0x48),unaff_EDI);
      *(undefined4 *)(param_1 + 0x48) = *extraout_EAX;
      *(undefined4 *)(param_1 + 0x4c) = extraout_EAX[1];
      *(undefined4 *)(param_1 + 0x50) = extraout_EAX[2];
      *(undefined4 *)(param_1 + 0x54) = extraout_EAX[3];
    }
    *(float *)(param_1 + 0x38) = *(float *)param_2 + *(float *)(param_1 + 0x38);
    *(float *)(param_1 + 0x3c) = *(float *)((int)param_2 + 4) + *(float *)(param_1 + 0x3c);
    *(float *)(param_1 + 0x40) = *(float *)((int)param_2 + 8) + *(float *)(param_1 + 0x40);
  }
  return;
}
