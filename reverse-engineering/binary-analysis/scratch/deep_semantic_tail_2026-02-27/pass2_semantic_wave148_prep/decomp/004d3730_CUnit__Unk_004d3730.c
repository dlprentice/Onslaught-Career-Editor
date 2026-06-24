/* address: 0x004d3730 */
/* name: CUnit__Unk_004d3730 */
/* signature: void __fastcall CUnit__Unk_004d3730(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CUnit__Unk_004d3730(void *param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float unaff_ESI;
  float10 fVar4;
  float10 fVar5;
  float10 fVar6;
  float10 fVar7;
  float10 fVar8;
  float10 fVar9;
  float10 fVar10;
  float10 fVar11;
  float10 fVar12;
  float fStack_50;
  float fStack_48;
  undefined4 uStack_34;
  undefined1 auStack_30 [4];
  float fStack_2c;
  float fStack_1c;
  float fStack_c;

  fVar12 = (float10)fpatan((float10)*(float *)((int)param_1 + 600) -
                           (float10)*(float *)((int)param_1 + 0x1c),
                           (float10)*(float *)((int)param_1 + 0x25c) -
                           (float10)*(float *)((int)param_1 + 0x20));
  fVar1 = *(float *)((int)param_1 + 0x260);
  fVar2 = *(float *)((int)param_1 + 0x24);
  fVar3 = *(float *)(*(int *)((int)param_1 + 0x164) + 0xb4) * _DAT_005d8584;
  fVar4 = (float10)(**(code **)(*(int *)param_1 + 0xb4))();
  fVar5 = (float10)*(float *)((int)param_1 + 600) - (float10)*(float *)((int)param_1 + 0x1c);
  fVar6 = (float10)*(float *)((int)param_1 + 0x25c) - (float10)*(float *)((int)param_1 + 0x20);
  fStack_50 = 99999.0;
  fVar7 = (float10)_DAT_005d85c8;
  fVar8 = fVar4 * (float10)(fVar1 - fVar2);
  do {
    fVar9 = (float10)fsin(fVar7);
    fVar9 = fVar9 * (float10)fVar3;
    fVar10 = fVar9 * fVar9 + (float10)(float)(fVar8 + fVar8);
    if ((float10)_DAT_005d856c < fVar10) {
      fVar11 = (float10)fcos(fVar7);
      fVar9 = fVar11 * (float10)fVar3 * ((SQRT(fVar10) - fVar9) / fVar4);
      if (((float10)_DAT_005d856c < fVar9) &&
         (fVar9 = ABS(fVar9 - SQRT(fVar5 * fVar5 + fVar6 * fVar6)), fVar9 < (float10)fStack_50)) {
        fStack_50 = (float)fVar9;
        fStack_48 = (float)fVar7;
      }
    }
    fVar7 = fVar7 + (float10)_DAT_005d8cb8;
  } while (fVar7 < (float10)_DAT_005d856c);
  CSquadNormal__Helper_004062d0(auStack_30,(void *)(float)-fVar12,fStack_48,0.0,unaff_ESI);
  *(float *)((int)param_1 + 0x7c) = fStack_2c * fVar3;
  *(float *)((int)param_1 + 0x80) = fStack_1c * fVar3;
  *(float *)((int)param_1 + 0x84) = fStack_c * fVar3;
  *(undefined4 *)((int)param_1 + 0x88) = uStack_34;
  return;
}
