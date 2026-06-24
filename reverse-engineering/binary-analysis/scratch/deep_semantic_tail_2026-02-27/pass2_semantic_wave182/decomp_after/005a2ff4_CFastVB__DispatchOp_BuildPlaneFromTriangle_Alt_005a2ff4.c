/* address: 0x005a2ff4 */
/* name: CFastVB__DispatchOp_BuildPlaneFromTriangle_Alt_005a2ff4 */
/* signature: void __stdcall CFastVB__DispatchOp_BuildPlaneFromTriangle_Alt_005a2ff4(void * param_1, void * param_2, void * param_3, void * param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void CFastVB__DispatchOp_BuildPlaneFromTriangle_Alt_005a2ff4
               (void *param_1,void *param_2,void *param_3,void *param_4)

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
  float fVar10;
  undefined1 auVar11 [16];
  undefined1 auVar12 [16];

  fVar1 = *(float *)((int)param_2 + 8);
  fVar9 = (float)*(undefined8 *)param_2;
  fVar10 = (float)((ulonglong)*(undefined8 *)param_2 >> 0x20);
  fVar2 = fVar1 - *(float *)((int)param_3 + 8);
  fVar4 = fVar9 - (float)*(undefined8 *)param_3;
  fVar5 = fVar10 - (float)((ulonglong)*(undefined8 *)param_3 >> 0x20);
  fVar6 = fVar1 - *(float *)((int)param_4 + 8);
  fVar7 = fVar9 - (float)*(undefined8 *)param_4;
  fVar8 = fVar10 - (float)((ulonglong)*(undefined8 *)param_4 >> 0x20);
  fVar3 = fVar6 * fVar5 - fVar2 * fVar8;
  fVar2 = fVar7 * fVar2 - fVar4 * fVar6;
  fVar4 = fVar8 * fVar4 - fVar5 * fVar7;
  fVar7 = fVar4 * fVar4;
  fVar5 = fVar3 * fVar3 + fVar7;
  fVar6 = fVar2 * fVar2 + 0.0;
  auVar11._4_4_ = fVar5;
  auVar11._0_4_ = fVar6;
  auVar11._8_4_ = fVar5;
  auVar11._12_4_ = fVar5;
  auVar12._4_4_ = fVar6;
  auVar12._0_4_ = fVar5 + fVar6;
  auVar12._8_4_ = fVar7 + fVar7;
  auVar12._12_4_ = 0;
  auVar12 = rsqrtss(auVar11,auVar12);
  fVar7 = auVar12._0_4_;
  fVar5 = _DAT_0065e7c0 * fVar7 * (_DAT_0065e7d0 - (fVar5 + fVar6) * fVar7 * fVar7);
  *(float *)param_1 = fVar3 * fVar5;
  *(float *)((int)param_1 + 4) = fVar2 * fVar5;
  *(float *)((int)param_1 + 8) = fVar4 * fVar5;
  *(float *)((int)param_1 + 0xc) = fVar5 * 0.0;
  *(uint *)((int)param_1 + 0xc) =
       (uint)(fVar3 * fVar5 * fVar9 + fVar4 * fVar5 * fVar1 + fVar2 * fVar5 * fVar10) ^
       _DAT_0065e7b0;
  return;
}
