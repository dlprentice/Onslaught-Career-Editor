/* address: 0x00570cb0 */
/* name: CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0 */
/* signature: bool __stdcall CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0(int param_1, void * param_2, void * param_3, void * param_4) */


bool CFastVB__SelectNextStripCandidateFromEdgeChain_00570cb0
               (int param_1,void *param_2,void *param_3,void *param_4)

{
  int iVar1;
  void *pvVar2;
  void *pvVar3;
  void *this;
  int iVar4;
  int iVar5;
  int iVar6;
  int unaff_EDI;

  this = param_3;
  if (*(char *)((int)param_3 + 8) == '\0') {
    iVar6 = *(int *)(*(int *)((int)param_3 + 4) + 0xc);
  }
  else {
    iVar6 = *(int *)(*(int *)((int)param_3 + 4) + 0x10);
  }
  param_3 = (void *)0x0;
  iVar1 = *(int *)(*(int *)((int)param_2 + 4) + iVar6 * 4);
  do {
    pvVar3 = param_3;
    if (iVar1 == 0) {
LAB_00570d6e:
      param_3 = pvVar3;
      *(void **)param_4 = param_3;
      *(int *)((int)param_4 + 4) = iVar1;
      if (iVar1 != 0) {
        iVar5 = CFastVB__HasAdjacentFaceTouchingPivotVertex_00570a90
                          (this,(int)param_3,param_2,unaff_EDI);
        if ((char)iVar5 != '\0') {
          *(bool *)((int)param_4 + 8) = *(int *)(iVar1 + 0xc) == iVar6;
          return param_3 != (void *)0x0;
        }
        *(bool *)((int)param_4 + 8) = *(int *)(iVar1 + 0x10) == iVar6;
      }
      return param_3 != (void *)0x0;
    }
    pvVar2 = *(void **)(iVar1 + 4);
    pvVar3 = *(void **)(iVar1 + 8);
    if (pvVar2 == (void *)0x0) {
LAB_00570d1e:
      if (pvVar3 != (void *)0x0) {
        iVar5 = *(int *)((int)this + 0x20);
        if (iVar5 < 0) {
          iVar4 = *(int *)((int)pvVar3 + 0xc);
        }
        else {
          iVar4 = *(int *)((int)pvVar3 + 0x10);
        }
        if ((((iVar4 != *(int *)((int)this + 0x1c)) && (pvVar2 != (void *)0x0)) &&
            (*(int *)((int)pvVar2 + 0xc) < 0)) &&
           ((pvVar3 = pvVar2, iVar5 < 0 || (*(int *)((int)pvVar2 + 0x14) != iVar5))))
        goto LAB_00570d6e;
      }
    }
    else {
      iVar5 = *(int *)((int)this + 0x20);
      if (iVar5 < 0) {
        iVar4 = *(int *)((int)pvVar2 + 0xc);
      }
      else {
        iVar4 = *(int *)((int)pvVar2 + 0x10);
      }
      if (iVar4 == *(int *)((int)this + 0x1c)) goto LAB_00570d1e;
      if (pvVar3 != (void *)0x0) {
        if ((-1 < *(int *)((int)pvVar3 + 0xc)) ||
           ((-1 < iVar5 && (*(int *)((int)pvVar3 + 0x14) == iVar5)))) goto LAB_00570d1e;
        goto LAB_00570d6e;
      }
    }
    if (*(int *)(iVar1 + 0xc) == iVar6) {
      iVar1 = *(int *)(iVar1 + 0x14);
    }
    else {
      iVar1 = *(int *)(iVar1 + 0x18);
    }
  } while( true );
}
