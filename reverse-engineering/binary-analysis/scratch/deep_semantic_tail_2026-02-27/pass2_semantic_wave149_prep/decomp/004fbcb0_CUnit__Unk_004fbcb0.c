/* address: 0x004fbcb0 */
/* name: CUnit__Unk_004fbcb0 */
/* signature: int __fastcall CUnit__Unk_004fbcb0(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

int __fastcall CUnit__Unk_004fbcb0(void *param_1)

{
  float fVar1;
  void *pvVar2;
  int iVar3;
  float *extraout_EAX;
  undefined4 *extraout_EAX_00;
  int iVar4;
  int iVar5;
  undefined4 *puVar6;
  void *unaff_EDI;
  undefined4 *puVar7;
  char *pcVar8;
  void *pvVar9;
  float local_80;
  float fStack_7c;
  float fStack_78;
  float fStack_74;
  undefined1 auStack_70 [16];
  undefined4 local_60 [12];
  undefined1 auStack_30 [48];

  if ((*(int *)(*(int *)((int)param_1 + 0x164) + 0x108) == 0) ||
     (*(int *)((int)param_1 + 0x244) == 4)) {
    if (*(int *)((int)param_1 + 0x140) == 0) {
      if (*(int *)((int)param_1 + 0x144) != 0) {
        if (((*(int *)((int)param_1 + 0x168) != 1) && (*(int *)((int)param_1 + 0x1e8) == 0)) &&
           (iVar5 = CUnit__Helper_004e43d0(*(int *)((int)param_1 + 0x144)), iVar5 != 0)) {
          fVar1 = *(float *)(*(int *)(*(int *)((int)param_1 + 0x144) + 0x3d0) + 0x34) + DAT_00672fd0
          ;
          *(undefined4 *)((int)param_1 + 0x1e8) = 0;
          *(undefined4 *)((int)param_1 + 0x168) = 1;
          *(float *)((int)param_1 + 0x16c) = fVar1;
        }
        return 1;
      }
    }
    else {
      iVar5 = 1;
      if (((*(int *)((int)param_1 + 0x168) != 1) && (*(int *)((int)param_1 + 0x1e8) == 0)) &&
         (iVar3 = CUnit__Helper_00509f70(*(int *)((int)param_1 + 0x140)), iVar3 != 0)) {
        iVar3 = *(int *)((int)param_1 + 0x140);
        fVar1 = _DAT_005d856c;
        if (iVar3 != 0) {
          fVar1 = *(float *)(*(int *)(iVar3 + 0xa0) + 0x88);
        }
        fVar1 = DAT_00672fd0 + fVar1;
        *(undefined4 *)((int)param_1 + 0x168) = 1;
        *(undefined4 *)((int)param_1 + 0x1ec) = 1;
        *(float *)((int)param_1 + 0x16c) = fVar1;
        pvVar2 = *(void **)(*(int *)(iVar3 + 0xa0) + 0x10);
        if (pvVar2 != (void *)0x0) {
          CMonitor__Helper_004e1940(&DAT_00896988,pvVar2,param_1);
        }
        if (*(int *)(*(int *)(*(int *)((int)param_1 + 0x140) + 0xa0) + 8) != 0) {
          do {
            (**(code **)(*(int *)param_1 + 0x160))(0x1d,iVar5,&local_80,local_60);
            if (local_80 == _DAT_005d856c) {
              if (((fStack_7c == _DAT_005d856c) && (fStack_78 == _DAT_005d856c)) && (iVar5 == 1)) {
                OID__Helper_0044a850(*(void **)((int)param_1 + 0x140),(int)auStack_70,unaff_EDI);
                local_80 = *extraout_EAX;
                fStack_7c = extraout_EAX[1];
                fStack_78 = extraout_EAX[2];
                fStack_74 = extraout_EAX[3];
                OID__Helper_0044a930(*(void **)((int)param_1 + 0x140),(int)auStack_30,unaff_EDI);
                puVar6 = extraout_EAX_00;
                puVar7 = local_60;
                for (iVar3 = 0xc; iVar3 != 0; iVar3 = iVar3 + -1) {
                  *puVar7 = *puVar6;
                  puVar6 = puVar6 + 1;
                  puVar7 = puVar7 + 1;
                }
              }
              if (((local_80 != _DAT_005d856c) || (fStack_7c != _DAT_005d856c)) ||
                 (fStack_78 != _DAT_005d856c)) goto LAB_004fbe9b;
            }
            else {
LAB_004fbe9b:
              CParticleManager__CreateEffect
                        (*(undefined4 *)(*(int *)(*(int *)((int)param_1 + 0x140) + 0xa0) + 8),
                         *(undefined4 *)((int)param_1 + 0x1ac),DAT_00854d80,DAT_00854d84,
                         DAT_00854d88,DAT_00854d8c,0,0);
              pvVar2 = *(void **)(*(int *)((int)param_1 + 0x1ac) + 4);
              if (pvVar2 != (void *)0x0) {
                CUnit__Helper_004097a0(pvVar2,&local_80,unaff_EDI);
              }
              iVar3 = *(int *)(*(int *)((int)param_1 + 0x1ac) + 4);
              if (iVar3 != 0) {
                puVar6 = local_60;
                puVar7 = (undefined4 *)(iVar3 + 0x10);
                for (iVar4 = 0xc; iVar4 != 0; iVar4 = iVar4 + -1) {
                  *puVar7 = *puVar6;
                  puVar6 = puVar6 + 1;
                  puVar7 = puVar7 + 1;
                }
                *(undefined4 *)(iVar3 + 0xa0) = 1;
              }
            }
            iVar5 = iVar5 + 1;
          } while (((local_80 != _DAT_005d856c) || (fStack_7c != _DAT_005d856c)) ||
                  (fStack_78 != _DAT_005d856c));
        }
        if (*(float *)((int)param_1 + 0x16c) <= DAT_00672fd0) {
          *(undefined4 *)((int)param_1 + 0x1e8) = 1;
        }
        return 1;
      }
    }
  }
  else if (*(int *)((int)param_1 + 0x244) == 0) {
    iVar5 = *(int *)param_1;
    *(undefined4 *)((int)param_1 + 0x244) = 3;
    pvVar9 = (void *)0x1;
    pcVar8 = s_deploying_006239cc;
    pvVar2 = (void *)(**(code **)(**(int **)((int)param_1 + 0x30) + 0x24))(s_deploying_006239cc,1,0)
    ;
    iVar3 = FindAnimationIndex(pvVar2,(int)pcVar8,pvVar9);
    (**(code **)(iVar5 + 0xf0))(iVar3);
  }
  return 0;
}
