/* address: 0x00509c80 */
/* name: CBattleEngine__Helper_00509c80 */
/* signature: double __thiscall CBattleEngine__Helper_00509c80(void * this, int param_1, int param_2, float param_3, float param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

double __thiscall
CBattleEngine__Helper_00509c80(void *this,int param_1,int param_2,float param_3,float param_4)

{
  int iVar1;
  int *piVar2;
  void *pvVar3;
  void *pvVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  double dVar8;

  if ((((*(int *)((int)this + 0xa0) != 0) &&
       (iVar7 = *(int *)(*(int *)((int)this + 0xa0) + 0x18), iVar7 != 0)) &&
      (*(float *)(iVar7 + 0x3c) * _DAT_005d8c6c != _DAT_005d856c)) &&
     ((*(int *)(iVar7 + 0x50) == 0 && (*(int *)(iVar7 + 0x6c) == 0)))) {
    dVar8 = CUnit__Helper_005099a0(this,(void *)param_1,(float)param_2,param_3,param_4);
    return dVar8;
  }
  param_1 = (int)(longlong)ROUND(*(float *)((int)this + 0x60));
  iVar5 = param_1 / 100;
  iVar6 = 0;
  iVar7 = iVar5 * 4 + 0xc;
  iVar1 = *(int *)(iVar7 + *(int *)((int)this + 0xa4));
  pvVar3 = CSPtrSet__First(DAT_008553ec);
  while (pvVar3 != (void *)0x0) {
    if (iVar6 == iVar1) {
      if (pvVar3 != (void *)0x0) goto LAB_00509d6c;
      break;
    }
    iVar6 = iVar6 + 1;
    pvVar3 = CSPtrSet__Next(DAT_008553ec);
  }
  do {
    iVar5 = iVar5 + -1;
    iVar7 = iVar7 + -4;
    if (iVar5 < 0) {
      pvVar3 = (void *)0x0;
      goto LAB_00509d72;
    }
    pvVar3 = (void *)CBattleEngine__Helper_00509e40(*(int *)(iVar7 + *(int *)((int)this + 0xa4)));
  } while (pvVar3 == (void *)0x0);
LAB_00509d6c:
  pvVar4 = pvVar3;
  if (pvVar3 == (void *)0x0) {
LAB_00509d72:
    iVar7 = 0xc;
    do {
      iVar5 = 0;
      iVar1 = *(int *)(iVar7 + *(int *)((int)this + 0xa4));
      piVar2 = (int *)*DAT_008553ec;
      DAT_008553ec[2] = (int)piVar2;
      if (piVar2 == (int *)0x0) {
        pvVar4 = (void *)0x0;
      }
      else {
        pvVar4 = (void *)*piVar2;
      }
      while (pvVar4 != (void *)0x0) {
        if (iVar5 == iVar1) {
          if (pvVar4 != (void *)0x0) goto LAB_00509dd5;
          break;
        }
        iVar5 = iVar5 + 1;
        piVar2 = *(int **)(DAT_008553ec[2] + 4);
        DAT_008553ec[2] = (int)piVar2;
        if (piVar2 == (int *)0x0) {
          pvVar4 = (void *)0x0;
        }
        else {
          pvVar4 = (void *)*piVar2;
        }
      }
      iVar7 = iVar7 + 4;
      pvVar4 = pvVar3;
    } while (iVar7 < 0x20);
  }
LAB_00509dd5:
  if ((pvVar4 == (void *)0x0) || (iVar7 = *(int *)((int)pvVar4 + 0x18), iVar7 == 0)) {
    return (double)_DAT_005d856c;
  }
  if (*(int *)(iVar7 + 0x50) != 0) {
    return (double)*(float *)((int)pvVar4 + 0x78);
  }
  if ((_DAT_005d856c < *(float *)(iVar7 + 0x28)) && (*(int *)(iVar7 + 0x48) != 0)) {
    return (double)*(float *)((int)pvVar4 + 0x9c);
  }
  return (double)(*(float *)(iVar7 + 0x2c) * *(float *)(iVar7 + 0x24));
}
