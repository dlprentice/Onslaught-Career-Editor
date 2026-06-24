/* address: 0x005a32d4 */
/* name: CFastVB__DispatchOp_MultiplyMatrix4x4_005a32d4 */
/* signature: void __stdcall CFastVB__DispatchOp_MultiplyMatrix4x4_005a32d4(void * param_1, void * param_2, void * param_3) */


void CFastVB__DispatchOp_MultiplyMatrix4x4_005a32d4(void *param_1,void *param_2,void *param_3)

{
  undefined8 uVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  float fVar5;
  float fVar6;
  float fVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  float fVar17;
  float fVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  float fVar22;
  float fVar23;
  float fVar24;
  float fVar25;
  float fVar26;
  float fVar27;
  float fVar28;
  float fVar29;
  float fVar30;
  float fVar31;
  float fVar32;
  float fVar33;
  float fVar34;
  float fVar35;
  float fVar36;

  uVar1 = *(undefined8 *)((int)param_3 + 0x30);
  fVar21 = (float)uVar1;
  fVar22 = (float)((ulonglong)uVar1 >> 0x20);
  fVar18 = *(float *)((int)param_3 + 0x30);
  fVar19 = *(float *)((int)param_3 + 0x34);
  fVar20 = *(float *)((int)param_3 + 0x38);
  fVar23 = (float)*(undefined8 *)((int)param_3 + 0x38);
  fVar24 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x38) >> 0x20);
  fVar2 = *(float *)((int)param_2 + 0xc);
  fVar3 = *(float *)((int)param_2 + 8);
  fVar4 = *(float *)((int)param_2 + 4);
  fVar33 = (float)*(undefined8 *)((int)param_3 + 0x20);
  fVar34 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x20) >> 0x20);
  fVar35 = (float)*(undefined8 *)((int)param_3 + 0x28);
  fVar36 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x28) >> 0x20);
  fVar5 = *(float *)param_2;
  fVar29 = (float)*(undefined8 *)((int)param_3 + 0x10);
  fVar30 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x10) >> 0x20);
  fVar31 = (float)*(undefined8 *)((int)param_3 + 0x18);
  fVar32 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 0x18) >> 0x20);
  fVar6 = *(float *)((int)param_2 + 0x1c);
  fVar7 = *(float *)((int)param_2 + 0x18);
  fVar25 = (float)*(undefined8 *)param_3;
  fVar26 = (float)((ulonglong)*(undefined8 *)param_3 >> 0x20);
  fVar27 = (float)*(undefined8 *)((int)param_3 + 8);
  fVar28 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 8) >> 0x20);
  fVar8 = *(float *)((int)param_2 + 0x14);
  fVar9 = *(float *)((int)param_2 + 0x10);
  fVar10 = *(float *)((int)param_2 + 0x2c);
  fVar11 = *(float *)((int)param_2 + 0x28);
  fVar12 = *(float *)((int)param_2 + 0x24);
  fVar13 = *(float *)((int)param_2 + 0x20);
  fVar14 = *(float *)((int)param_2 + 0x3c);
  fVar15 = *(float *)((int)param_2 + 0x38);
  fVar16 = *(float *)((int)param_2 + 0x34);
  fVar17 = *(float *)((int)param_2 + 0x30);
  *(ulonglong *)param_1 =
       CONCAT44(fVar9 * fVar25 + fVar8 * fVar29 + fVar7 * fVar33 + fVar6 * fVar21,
                fVar5 * fVar25 + fVar4 * fVar29 + fVar3 * fVar33 + fVar2 * fVar21);
  *(ulonglong *)((int)param_1 + 8) =
       CONCAT44(fVar17 * fVar25 + fVar16 * fVar29 + fVar15 * fVar33 + fVar14 * fVar18,
                fVar13 * fVar25 + fVar12 * fVar29 + fVar11 * fVar33 + fVar10 * fVar18);
  *(ulonglong *)((int)param_1 + 0x10) =
       CONCAT44(fVar9 * fVar26 + fVar8 * fVar30 + fVar7 * fVar34 + fVar6 * fVar22,
                fVar5 * fVar26 + fVar4 * fVar30 + fVar3 * fVar34 + fVar2 * fVar22);
  *(ulonglong *)((int)param_1 + 0x18) =
       CONCAT44(fVar17 * fVar26 + fVar16 * fVar30 + fVar15 * fVar34 + fVar14 * fVar19,
                fVar13 * fVar26 + fVar12 * fVar30 + fVar11 * fVar34 + fVar10 * fVar19);
  *(ulonglong *)((int)param_1 + 0x20) =
       CONCAT44(fVar9 * fVar27 + fVar8 * fVar31 + fVar7 * fVar35 + fVar6 * fVar23,
                fVar5 * fVar27 + fVar4 * fVar31 + fVar3 * fVar35 + fVar2 * fVar23);
  *(ulonglong *)((int)param_1 + 0x28) =
       CONCAT44(fVar17 * fVar27 + fVar16 * fVar31 + fVar15 * fVar35 + fVar14 * fVar20,
                fVar13 * fVar27 + fVar12 * fVar31 + fVar11 * fVar35 + fVar10 * fVar20);
  *(ulonglong *)((int)param_1 + 0x30) =
       CONCAT44(fVar9 * fVar28 + fVar8 * fVar32 + fVar7 * fVar36 + fVar6 * fVar24,
                fVar5 * fVar28 + fVar4 * fVar32 + fVar3 * fVar36 + fVar2 * fVar24);
  *(ulonglong *)((int)param_1 + 0x38) =
       CONCAT44(fVar17 * fVar28 + fVar16 * fVar32 + fVar15 * fVar36 + fVar14 * fVar24,
                fVar13 * fVar28 + fVar12 * fVar32 + fVar11 * fVar36 + fVar10 * fVar24);
  return;
}
