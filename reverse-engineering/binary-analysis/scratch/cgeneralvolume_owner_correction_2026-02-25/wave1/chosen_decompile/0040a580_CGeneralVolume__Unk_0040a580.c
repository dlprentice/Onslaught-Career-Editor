/* address: 0x0040a580 */
/* name: CGeneralVolume__Unk_0040a580 */
/* signature: void __fastcall CGeneralVolume__Unk_0040a580(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CGeneralVolume__Unk_0040a580(void *param_1)

{
  bool bVar1;
  int iVar2;
  undefined3 extraout_var;
  int *piVar3;
  int unaff_EDI;
  float10 fVar4;
  undefined4 uVar5;
  void *local_4;

  if ((*(int *)((int)param_1 + 0x58c) != 0) || (*(int *)((int)param_1 + 0x260) != 2)) {
    *(undefined4 *)((int)param_1 + 0x588) = 0;
    if ((*(int *)((int)param_1 + 0x260) != 1) && (*(int *)((int)param_1 + 0x260) != 0)) {
      local_4 = param_1;
      iVar2 = CGeneralVolume__Unk_00411b70(*(int *)((int)param_1 + 0x57c));
      if (iVar2 != 1) {
        bVar1 = CGeneralVolume__Unk_004135d0(*(int *)((int)param_1 + 0x578));
        if (CONCAT31(extraout_var,bVar1) != 1) {
          CMonitor__Unk_00414010();
          CMonitor__Unk_00412000(*(void **)((int)param_1 + 0x57c));
          *(undefined4 *)((int)param_1 + 0x2cc) = 0x3f800000;
          if (*(int *)((int)param_1 + 0x260) == 3) {
            local_4 = (void *)(DAT_00672fd0 + _DAT_005d85ec);
            CEventManager__AddEvent_AtTime
                      (&EVENT_MANAGER,0x1771,param_1,(float *)&local_4,0,(void *)0x0,(void *)0x0);
            iVar2 = (**(code **)(*(int *)param_1 + 0x10c))();
            if (iVar2 == 0) {
              *(undefined4 *)((int)param_1 + 0x520) = 0;
            }
            else {
              *(float *)((int)param_1 + 0x520) = DAT_00672fd0;
            }
            if (*(int *)((int)param_1 + 0x528) != 0) {
              CGeneralVolume__Helper_00424920(*(int *)((int)param_1 + 0x528));
            }
            *(undefined4 *)((int)param_1 + 0x260) = 0;
            CUnit__Unk_004f4560(param_1,s_flytowalk_006234bc,1,0,unaff_EDI);
            if (*(int *)((int)param_1 + 0x59c) != 0) {
              piVar3 = CSoundManager__Unk_004e1880
                                 (&DAT_00896988,*(int *)((int)param_1 + 0x59c) + 0x40,param_1,
                                  unaff_EDI);
              if (piVar3 != (int *)0x0) {
                CSoundManager__Unk_004e1260(&DAT_00896988,piVar3[3],0,0.02,(float)param_1,unaff_EDI)
                ;
              }
            }
            CSoundManager__Unk_004e1940(&DAT_00896988,*(void **)((int)param_1 + 0x5a0),param_1);
            *(undefined4 *)((int)param_1 + 0x304) = 0;
            return;
          }
          if (*(float *)(*(int *)((int)param_1 + 0x4b0) + 0x2c) <= *(float *)((int)param_1 + 0xfc))
          {
            fVar4 = (float10)(**(code **)(*(int *)param_1 + 0x13c))();
            if ((float10)_DAT_005d856c < fVar4) {
              uVar5 = *(undefined4 *)((int)param_1 + 0x138);
              fVar4 = (float10)(**(code **)(*(int *)param_1 + 0x13c))(uVar5);
              CInfluenceMapManager__FindNearestMap
                        (*(undefined4 *)((int)param_1 + 0x1c),*(undefined4 *)((int)param_1 + 0x20),
                         (float)fVar4,uVar5);
            }
            *(undefined4 *)((int)param_1 + 0x304) = 0;
            if (*(int *)((int)param_1 + 0x528) != 0) {
              CGeneralVolume__Helper_00424990(*(int *)((int)param_1 + 0x528));
            }
            *(undefined4 *)((int)param_1 + 0x260) = 1;
            CBattleEngine__Unk_00406460((int)param_1);
            CUnit__Unk_004f4560(param_1,s_walktofly_006234b0,1,0,unaff_EDI);
            if (_DAT_005d8bb8 <= DAT_00672fd0 - *(float *)((int)param_1 + 0xcc)) {
              *(undefined4 *)((int)param_1 + 0x2f0) = 0x47c34f80;
              local_4 = (void *)(DAT_00672fd0 + _DAT_005d85c0);
              CEventManager__AddEvent_AtTime
                        (&EVENT_MANAGER,6000,param_1,(float *)&local_4,0,(void *)0x0,(void *)0x0);
            }
            else {
              *(undefined4 *)((int)param_1 + 0x2f0) = *(undefined4 *)((int)param_1 + 0x24);
            }
            *(float *)((int)param_1 + 0x2f4) = DAT_00672fd0;
            CSoundManager__Unk_004e1940(&DAT_00896988,*(void **)((int)param_1 + 0x5a4),param_1);
            if (*(int *)((int)param_1 + 0x59c) != 0) {
              iVar2 = CSoundManager__Unk_004e1ab0
                                (&DAT_00896988,*(int *)((int)param_1 + 0x59c),(int)param_1,unaff_EDI
                                );
              if (iVar2 == 0) {
                CSoundManager__Unk_004e1940(&DAT_00896988,*(void **)((int)param_1 + 0x59c),param_1);
                return;
              }
              piVar3 = CSoundManager__Unk_004e1880
                                 (&DAT_00896988,*(int *)((int)param_1 + 0x59c) + 0x40,param_1,
                                  unaff_EDI);
              if (piVar3 != (int *)0x0) {
                CSoundManager__Unk_004e1260
                          (&DAT_00896988,piVar3[3],0x3f800000,0.02,(float)param_1,unaff_EDI);
              }
            }
          }
        }
      }
    }
  }
  return;
}
