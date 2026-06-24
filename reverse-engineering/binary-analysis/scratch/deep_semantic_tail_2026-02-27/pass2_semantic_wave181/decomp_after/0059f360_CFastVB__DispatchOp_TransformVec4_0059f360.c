/* address: 0x0059f360 */
/* name: CFastVB__DispatchOp_TransformVec4_0059f360 */
/* signature: int __stdcall CFastVB__DispatchOp_TransformVec4_0059f360(void * param_1, void * param_2, void * param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int CFastVB__DispatchOp_TransformVec4_0059f360(void *param_1,void *param_2,void *param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  float fVar4;
  uint uVar5;
  uint uVar6;
  uint uVar7;
  float fVar8;
  float fVar9;
  float fVar10;
  float fVar11;
  float fVar12;
  float fVar13;
  float fVar14;

  uVar5 = (uint)*(undefined8 *)param_3;
  uVar6 = (uint)((ulonglong)*(undefined8 *)param_3 >> 0x20);
  uVar7 = (uint)*(undefined8 *)((int)param_3 + 8);
  fVar8 = (float)((ulonglong)*(undefined8 *)((int)param_3 + 8) >> 0x20);
  fVar1 = (float)*(undefined8 *)param_2;
  fVar2 = (float)((ulonglong)*(undefined8 *)param_2 >> 0x20);
  fVar3 = (float)*(undefined8 *)((int)param_2 + 8);
  fVar4 = (float)((ulonglong)*(undefined8 *)((int)param_2 + 8) >> 0x20);
  fVar9 = (float)(uVar5 ^ _UNK_005f42e8);
  fVar11 = (float)(uVar5 ^ _UNK_005f42ec);
  fVar13 = (float)(uVar6 ^ _UNK_005f42d8);
  fVar14 = (float)(uVar6 ^ _UNK_005f42dc);
  fVar10 = (float)(uVar7 ^ _UNK_005f42c8);
  fVar12 = (float)(uVar7 ^ _UNK_005f42cc);
  *(ulonglong *)param_1 =
       CONCAT44(fVar8 * fVar2 + (float)(uVar5 ^ _UNK_005f42e4) * fVar3 +
                (float)(uVar6 ^ _UNK_005f42d4) * fVar4 + (float)(uVar7 ^ _UNK_005f42c4) * fVar1,
                fVar8 * fVar1 + (float)(uVar5 ^ _DAT_005f42e0) * fVar4 +
                (float)(uVar6 ^ _DAT_005f42d0) * fVar3 + (float)(uVar7 ^ _DAT_005f42c0) * fVar2);
  *(ulonglong *)((int)param_1 + 8) =
       CONCAT44(fVar8 * fVar4 + fVar11 * fVar1 + fVar14 * fVar2 + fVar12 * fVar3,
                fVar8 * fVar3 + fVar9 * fVar2 + fVar13 * fVar1 + fVar10 * fVar4);
  return (int)param_1;
}
