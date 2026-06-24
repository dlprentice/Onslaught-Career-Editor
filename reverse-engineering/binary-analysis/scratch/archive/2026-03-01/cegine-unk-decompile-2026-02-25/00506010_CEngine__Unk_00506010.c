/* address: 0x00506010 */
/* name: CEngine__Unk_00506010 */
/* signature: int __fastcall CEngine__Unk_00506010(void * param_1) */


int __fastcall CEngine__Unk_00506010(void *param_1)

{
  int *piVar1;
  float fVar2;
  void *pvVar3;
  int iVar4;
  int iVar5;
  void *pvVar6;
  longlong local_8;

  iVar5 = 0;
  local_8 = (longlong)ROUND(*(float *)((int)param_1 + 0x60));
  *(undefined4 *)((int)param_1 + 0x60) = 0;
  *(int *)((int)param_1 + 0x68) = (int)(float)local_8 / 100;
  iVar4 = *(int *)(*(int *)((int)param_1 + 0xa4) + 0xc + ((int)(float)local_8 / 100) * 4);
  pvVar3 = CSPtrSet__First(DAT_008553ec);
  while (pvVar3 != (void *)0x0) {
    if (iVar5 == iVar4) goto LAB_0050607f;
    iVar5 = iVar5 + 1;
    piVar1 = *(int **)(*(int *)((int)DAT_008553ec + 8) + 4);
    *(int **)((int)DAT_008553ec + 8) = piVar1;
    if (piVar1 == (int *)0x0) {
      pvVar3 = (void *)0x0;
    }
    else {
      pvVar3 = (void *)*piVar1;
    }
  }
  pvVar3 = (void *)0x0;
LAB_0050607f:
  *(void **)((int)param_1 + 0xa0) = pvVar3;
  do {
    if (pvVar3 != (void *)0x0) {
      if (*(int *)((int)param_1 + 0xa0) == 0) {
        iVar4 = CEngine__Unk_00509e90((int)param_1);
        if (iVar4 == 0) {
          return 0;
        }
      }
      else if (DAT_00672fd0 <= *(float *)((int)param_1 + 100)) {
        return 0;
      }
      iVar4 = *(int *)((int)param_1 + 0xa0);
      if ((iVar4 != 0) && (*(int *)(iVar4 + 0x18) != 0)) {
        fVar2 = DAT_00672fd0 + *(float *)(iVar4 + 0x38);
        *(undefined4 *)((int)param_1 + 0x6c) = 0;
        *(float *)((int)param_1 + 100) = fVar2;
        if ((*(byte *)(*(int *)((int)param_1 + 8) + 0x34) & 8) != 0) {
          *(undefined4 *)(*(int *)((int)param_1 + 8) + 0x5e0) = 0;
        }
        iVar4 = CEngine__Unk_005069f0(param_1);
        if (iVar4 != 0) {
          pvVar3 = *(void **)(*(int *)((int)param_1 + 0xa0) + 0xc);
          if ((pvVar3 != (void *)0x0) && (*(int *)(*(int *)((int)param_1 + 0xa0) + 0xb4) != 0)) {
            pvVar6 = *(void **)((int)param_1 + 8);
            if ((*(byte *)((int)pvVar6 + 0x34) & 8) != 0) {
              pvVar6 = (void *)0x0;
            }
            CSoundManager__Unk_004e1940(&DAT_00896988,pvVar3,pvVar6);
          }
        }
        if (0 < *(int *)(*(int *)((int)param_1 + 0xa0) + 0x44)) {
          *(undefined4 *)((int)param_1 + 0x6c) = 1;
          local_8 = CONCAT44(local_8._4_4_,
                             DAT_00672fd0 + *(float *)(*(int *)((int)param_1 + 0xa0) + 0x3c));
          CEventManager__AddEvent_AtTime
                    (&EVENT_MANAGER,0x1389,param_1,(float *)&local_8,0,(void *)0x0,(void *)0x0);
        }
        return 1;
      }
      return 0;
    }
    iVar4 = *(int *)((int)param_1 + 0x68) + -1;
    *(int *)((int)param_1 + 0x68) = iVar4;
    if (iVar4 < 0) {
      return 0;
    }
    iVar5 = 0;
    iVar4 = *(int *)(*(int *)((int)param_1 + 0xa4) + 0xc + iVar4 * 4);
    pvVar3 = CSPtrSet__First(DAT_008553ec);
    while (pvVar3 != (void *)0x0) {
      if (iVar5 == iVar4) goto LAB_005060d1;
      iVar5 = iVar5 + 1;
      piVar1 = *(int **)(*(int *)((int)DAT_008553ec + 8) + 4);
      *(int **)((int)DAT_008553ec + 8) = piVar1;
      if (piVar1 == (int *)0x0) {
        pvVar3 = (void *)0x0;
      }
      else {
        pvVar3 = (void *)*piVar1;
      }
    }
    pvVar3 = (void *)0x0;
LAB_005060d1:
    *(void **)((int)param_1 + 0xa0) = pvVar3;
  } while( true );
}
