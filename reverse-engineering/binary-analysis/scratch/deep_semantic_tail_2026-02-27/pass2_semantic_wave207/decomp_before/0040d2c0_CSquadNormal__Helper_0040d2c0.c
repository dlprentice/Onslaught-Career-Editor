/* address: 0x0040d2c0 */
/* name: CSquadNormal__Helper_0040d2c0 */
/* signature: void __thiscall CSquadNormal__Helper_0040d2c0(void * this, void * param_1, void * param_2, void * param_3) */


void __thiscall CSquadNormal__Helper_0040d2c0(void *this,void *param_1,void *param_2,void *param_3)

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
  float fVar11;
  float fVar12;

  fVar1 = *(float *)((int)this + 0x28);
  fVar2 = *(float *)((int)param_2 + 8);
  fVar3 = *(float *)((int)this + 0x24);
  fVar4 = *(float *)((int)param_2 + 4);
  fVar5 = *(float *)((int)this + 0x20);
  fVar6 = *(float *)param_2;
  fVar7 = *(float *)((int)this + 0x18);
  fVar8 = *(float *)((int)param_2 + 8);
  fVar9 = *(float *)((int)this + 0x14);
  fVar10 = *(float *)((int)param_2 + 4);
  fVar11 = *(float *)((int)this + 0x10);
  fVar12 = *(float *)param_2;
  *(float *)param_1 =
       *(float *)param_2 * *(float *)this +
       *(float *)((int)this + 4) * *(float *)((int)param_2 + 4) +
       *(float *)((int)this + 8) * *(float *)((int)param_2 + 8);
  *(float *)((int)param_1 + 4) = fVar11 * fVar12 + fVar9 * fVar10 + fVar7 * fVar8;
  *(float *)((int)param_1 + 8) = fVar5 * fVar6 + fVar3 * fVar4 + fVar1 * fVar2;
  return;
}
