/* address: 0x005a30f4 */
/* name: CFastVB__DispatchOp_QuaternionToMatrix4_Alt_005a30f4 */
/* signature: void __stdcall CFastVB__DispatchOp_QuaternionToMatrix4_Alt_005a30f4(void * param_1, void * param_2) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__DispatchOp_QuaternionToMatrix4_Alt_005a30f4(void *param_1,void *param_2)

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
  float fVar12;
  float fVar13;
  undefined1 auVar10 [16];
  undefined1 auVar11 [16];
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;

  fVar5 = (float)*(undefined8 *)param_2;
  fVar6 = (float)((ulonglong)*(undefined8 *)param_2 >> 0x20);
  fVar7 = (float)*(undefined8 *)((int)param_2 + 8);
  fVar8 = (float)((ulonglong)*(undefined8 *)((int)param_2 + 8) >> 0x20);
  fVar1 = (float)((uint)fVar5 & _DAT_0065e850);
  fVar2 = (float)((uint)fVar6 & uRam0065e854);
  fVar3 = (float)((uint)fVar7 & uRam0065e858);
  fVar4 = (float)((uint)fVar8 & uRam0065e85c);
  fVar3 = fVar3 * fVar3;
  fVar4 = fVar4 * fVar4;
  fVar1 = fVar1 * fVar1 + fVar3;
  fVar2 = fVar2 * fVar2 + fVar4;
  auVar10._4_4_ = fVar1;
  auVar10._0_4_ = fVar2;
  auVar10._8_4_ = fVar1;
  auVar10._12_4_ = fVar1;
  auVar11._4_4_ = fVar2;
  auVar11._0_4_ = fVar1 + fVar2;
  auVar11._8_4_ = fVar3 + fVar3;
  auVar11._12_4_ = fVar4 + fVar4;
  auVar11 = rsqrtss(auVar10,auVar11);
  fVar3 = auVar11._0_4_;
  fVar1 = DAT_0065e830 * fVar3 * (DAT_0065e840 - (fVar1 + fVar2) * fVar3 * fVar3);
  fVar5 = fVar5 * fVar1;
  fVar6 = fVar6 * fVar1;
  fVar7 = fVar7 * fVar1;
  fVar8 = fVar8 * fVar1;
  fVar1 = _DAT_0065e810 * fVar5;
  fVar2 = fRam0065e814 * fVar6;
  fVar3 = fRam0065e818 * fVar7;
  fVar4 = fRam0065e81c * fVar8;
  fVar9 = fVar1 * fVar6 + _DAT_0065e820;
  fVar12 = fVar2 * fVar6 + fRam0065e824;
  fVar13 = fVar3 * fVar6 + fRam0065e828;
  fVar6 = fVar4 * fVar6 + fRam0065e82c;
  fVar14 = fVar1 * fVar7 + _DAT_0065e800;
  fVar15 = fVar2 * fVar7 + fRam0065e804;
  fVar16 = fVar3 * fVar7 + fRam0065e808;
  fVar7 = fVar4 * fVar7 + fRam0065e80c;
  fVar17 = fVar1 * fVar8 + _DAT_0065e7f0;
  fVar18 = fVar2 * fVar8 + fRam0065e7f4;
  fVar19 = fVar3 * fVar8 + fRam0065e7f8;
  fVar8 = fVar4 * fVar8 + fRam0065e7fc;
  fVar2 = fVar2 * fVar5 + fRam0065e7e4;
  fVar3 = fVar3 * fVar5 + fRam0065e7e8;
  fVar4 = fVar4 * fVar5 + fRam0065e7ec;
  *(float *)param_1 = fVar1 * fVar5 + _DAT_0065e7e0;
  *(float *)((int)param_1 + 4) = fVar2;
  *(float *)((int)param_1 + 8) = fVar3;
  *(float *)((int)param_1 + 0xc) = fVar4;
  *(float *)((int)param_1 + 0x10) = fVar9;
  *(float *)((int)param_1 + 0x14) = fVar12;
  *(float *)((int)param_1 + 0x18) = fVar13;
  *(float *)((int)param_1 + 0x1c) = fVar6;
  *(float *)((int)param_1 + 0x20) = fVar14;
  *(float *)((int)param_1 + 0x24) = fVar15;
  *(float *)((int)param_1 + 0x28) = fVar16;
  *(float *)((int)param_1 + 0x2c) = fVar7;
  *(float *)((int)param_1 + 0x30) = fVar17;
  *(float *)((int)param_1 + 0x34) = fVar18;
  *(float *)((int)param_1 + 0x38) = fVar19;
  *(float *)((int)param_1 + 0x3c) = fVar8;
  return;
}
