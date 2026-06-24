/* address: 0x004fcc30 */
/* name: CThing__Helper_004fcc30 */
/* signature: void __thiscall CThing__Helper_004fcc30(void * this, void * param_1, int param_2, void * param_3) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall CThing__Helper_004fcc30(void *this,void *param_1,int param_2,void *param_3)

{
  float fVar1;
  float fVar2;
  float fVar3;
  bool bVar4;
  float *pfVar5;
  int iVar6;
  int iVar7;
  int unaff_EDI;
  float10 fVar8;

  if (*(void **)((int)this + 0x148) != (void *)0x0) {
    CThing__Helper_004e6640(*(void **)((int)this + 0x148),(int)this,(int)param_1,unaff_EDI);
  }
  if ((*(byte *)((int)param_1 + 0x34) & 0x10) != 0) {
    *(undefined4 *)((int)this + 0x248) = 1;
  }
  if (((((*(uint *)((int)param_1 + 0x34) & 0x100000) == 0) || (param_2 == 0)) ||
      (*(int *)param_2 == 0)) ||
     (fVar8 = (float10)(**(code **)(*(int *)this + 0xb4))(), fVar8 <= (float10)_DAT_005d856c))
  goto LAB_004fcda9;
  iVar6 = *(int *)(param_2 + 0x80);
  bVar4 = false;
  iVar7 = iVar6;
  pfVar5 = (float *)param_2;
  if (iVar6 < 1) {
LAB_004fccda:
    if (iVar6 < 2) goto LAB_004fcda9;
    fVar1 = *(float *)(param_2 + 8);
    fVar2 = *(float *)(param_2 + 0xc);
    fVar3 = *(float *)(param_2 + 0x10);
    iVar6 = 2;
    pfVar5 = (float *)(param_2 + 0x20);
    do {
      fVar1 = fVar1 + pfVar5[-2];
      fVar2 = fVar2 + pfVar5[-1];
      fVar3 = fVar3 + *pfVar5;
      pfVar5 = pfVar5 + 4;
      iVar6 = iVar6 + -1;
    } while (iVar6 != 0);
    fVar1 = SQRT(fVar2 * fVar2 + fVar1 * fVar1 + fVar3 * fVar3);
    if (fVar1 != _DAT_005d856c) {
      fVar3 = fVar3 * (_DAT_005d8568 / fVar1);
    }
    if (fVar3 * _DAT_005d8be0 <= _DAT_005dfb74) goto LAB_004fcda9;
  }
  else {
    do {
      if (_DAT_005dfb78 < pfVar5[4] * _DAT_005d8be0) {
        bVar4 = true;
      }
      iVar7 = iVar7 + -1;
      pfVar5 = pfVar5 + 4;
    } while (iVar7 != 0);
    if (!bVar4) goto LAB_004fccda;
  }
  (**(code **)(*(int *)this + 0x118))(param_1);
  (**(code **)(*(int *)this + 0x110))();
LAB_004fcda9:
  CComplexThing__Hit(this,(int)param_1,param_2);
  return;
}
