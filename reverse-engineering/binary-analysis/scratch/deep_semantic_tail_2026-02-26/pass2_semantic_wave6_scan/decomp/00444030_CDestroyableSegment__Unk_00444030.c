/* address: 0x00444030 */
/* name: CDestroyableSegment__Unk_00444030 */
/* signature: void __thiscall CDestroyableSegment__Unk_00444030(void * this, int param_1, int param_2, int param_3, int param_4) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __thiscall
CDestroyableSegment__Unk_00444030(void *this,int param_1,int param_2,int param_3,int param_4)

{
  float fVar1;
  bool bVar2;
  float fVar3;
  int iVar4;
  int *piVar5;
  double dVar6;

  if (param_1 != -1) {
    piVar5 = *(int **)(*(int *)((int)this + 4) + param_1 * 4);
    if (piVar5 == (int *)0x0) {
      piVar5 = *(int **)(*(int *)((int)this + 0x10) + 0x30);
      if (piVar5 == (int *)0x0) {
        return;
      }
      iVar4 = (**(code **)(*piVar5 + 0x24))();
      if (iVar4 == 0) {
        return;
      }
      CDestructableSegmentsController__Helper_004aa6b0(iVar4);
      CConsole__Printf(&DAT_0066f580,s_WARNING____s___building_part_not_00628614);
    }
    else {
      (**(code **)(*piVar5 + 0xc))(param_2,param_3);
      iVar4 = CDestroyableSegment__Unk_004433f0(*(int *)((int)this + 0xc));
      if ((iVar4 == 1) ||
         (fVar1 = *(float *)((int)this + 0x18), fVar3 = (float)_DAT_005db0a0,
         dVar6 = CDestroyableSegment__Helper_00442890(*(void **)((int)this + 0xc)),
         dVar6 < (double)(fVar1 * fVar3))) {
        (**(code **)(**(int **)((int)this + 0x10) + 200))();
      }
    }
  }
  if (*(int *)((int)this + 0x2c) != 1) {
    iVar4 = *(int *)((int)this + 8);
    bVar2 = true;
    fVar1 = _DAT_005d8568;
    if (0 < iVar4) {
      piVar5 = *(int **)((int)this + 4);
      do {
        if ((*piVar5 != 0) && (*(int *)(*piVar5 + 0x1c) == 1)) {
          bVar2 = false;
        }
        piVar5 = piVar5 + 1;
        iVar4 = iVar4 + -1;
      } while (iVar4 != 0);
      if (!bVar2) {
        dVar6 = CDestroyableSegment__Helper_00442890(*(void **)((int)this + 0xc));
        fVar1 = (float)dVar6;
      }
    }
    iVar4 = *(int *)((int)this + 8);
    bVar2 = true;
    fVar3 = _DAT_005d8568;
    if (0 < iVar4) {
      piVar5 = *(int **)((int)this + 4);
      do {
        if ((*piVar5 != 0) && (*(int *)(*piVar5 + 0x1c) == 1)) {
          bVar2 = false;
        }
        piVar5 = piVar5 + 1;
        iVar4 = iVar4 + -1;
      } while (iVar4 != 0);
      if (!bVar2) {
        fVar3 = *(float *)((int)this + 0x18);
      }
    }
    if (fVar1 < fVar3 * _DAT_005d85ec) {
      *(undefined4 *)((int)this + 0x2c) = 1;
    }
  }
  return;
}
