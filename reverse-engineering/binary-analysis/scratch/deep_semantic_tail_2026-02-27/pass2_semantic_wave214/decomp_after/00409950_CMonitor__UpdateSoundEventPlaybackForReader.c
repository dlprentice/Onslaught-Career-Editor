/* address: 0x00409950 */
/* name: CMonitor__UpdateSoundEventPlaybackForReader */
/* signature: void __fastcall CMonitor__UpdateSoundEventPlaybackForReader(void * param_1) */


/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void __fastcall CMonitor__UpdateSoundEventPlaybackForReader(void *param_1)

{
  float fVar1;
  float fVar2;
  float fVar3;
  int iVar4;
  int *piVar5;
  int unaff_ESI;
  int unaff_EDI;
  void *to_read;

  iVar4 = CMonitor__HasAnySoundEventForReaderChain
                    (&DAT_00896988,*(int *)((int)param_1 + 0x5c4),(int)param_1,unaff_ESI);
  if (iVar4 == 0) {
    CMonitor__PlayRandomSampleFromChain(&DAT_00896988,*(void **)((int)param_1 + 0x5c4),param_1);
  }
  if (_DAT_005d8c48 <= *(float *)((int)param_1 + 0xf8)) {
    if (_DAT_005d8ba0 <= *(float *)((int)param_1 + 0xfc)) {
      piVar5 = CMonitor__FindSoundEventByOwnerAndName
                         (&DAT_00896988,*(int *)((int)param_1 + 0x5ac) + 0x40,param_1,unaff_ESI);
      if (piVar5 != (int *)0x0) {
        CMonitor__Helper_004e1260(&DAT_00896988,piVar5[3],0,0.02,(float)param_1,unaff_ESI);
      }
      if ((*(int *)((int)param_1 + 0x5b0) != 0) &&
         (piVar5 = CMonitor__FindSoundEventByOwnerAndName
                             (&DAT_00896988,*(int *)((int)param_1 + 0x5b0) + 0x40,param_1,unaff_ESI)
         , piVar5 != (int *)0x0)) {
        CMonitor__Helper_004e1260(&DAT_00896988,piVar5[3],0,0.02,(float)param_1,unaff_ESI);
      }
      piVar5 = CMonitor__FindSoundEventByOwnerAndName
                         (&DAT_00896988,*(int *)((int)param_1 + 0x5a8) + 0x40,param_1,unaff_ESI);
      if (piVar5 != (int *)0x0) {
        CMonitor__Helper_004e1260(&DAT_00896988,piVar5[3],0,0.02,(float)param_1,unaff_ESI);
      }
    }
    else {
      CMonitor__StopSoundEventByOwnerAndName
                (&DAT_00896988,*(int *)((int)param_1 + 0x5a8) + 0x40,param_1,unaff_ESI);
      if (*(int *)((int)param_1 + 0x5b0) != 0) {
        CMonitor__StopSoundEventByOwnerAndName
                  (&DAT_00896988,*(int *)((int)param_1 + 0x5b0) + 0x40,param_1,unaff_ESI);
      }
      iVar4 = CMonitor__HasAnySoundEventForReaderChain
                        (&DAT_00896988,*(int *)((int)param_1 + 0x5ac),(int)param_1,unaff_ESI);
      if (iVar4 == 0) {
        CMonitor__PlayRandomSampleFromChain(&DAT_00896988,*(void **)((int)param_1 + 0x5ac),param_1);
      }
    }
  }
  else {
    CMonitor__StopSoundEventByOwnerAndName
              (&DAT_00896988,*(int *)((int)param_1 + 0x5ac) + 0x40,param_1,unaff_ESI);
    if (*(int *)((int)param_1 + 0x5b0) != 0) {
      CMonitor__StopSoundEventByOwnerAndName
                (&DAT_00896988,*(int *)((int)param_1 + 0x5b0) + 0x40,param_1,unaff_ESI);
    }
    iVar4 = CMonitor__HasAnySoundEventForReaderChain
                      (&DAT_00896988,*(int *)((int)param_1 + 0x5a8),(int)param_1,unaff_ESI);
    if (iVar4 == 0) {
      CMonitor__PlayRandomSampleFromChain(&DAT_00896988,*(void **)((int)param_1 + 0x5a8),param_1);
    }
  }
  if (*(int *)((int)param_1 + 0x5e4) != 0) {
    iVar4 = CMonitor__HasAnySoundEventForReaderChain
                      (&DAT_00896988,*(int *)((int)param_1 + 0x5b8),(int)param_1,unaff_ESI);
    if (iVar4 == 0) {
      CMonitor__PlayRandomSampleFromChain(&DAT_00896988,*(void **)((int)param_1 + 0x5b8),param_1);
    }
    *(undefined4 *)((int)param_1 + 0x5e4) = 0;
  }
  piVar5 = *(int **)((int)param_1 + 0x294);
  *(int **)((int)param_1 + 0x29c) = piVar5;
  if (piVar5 == (int *)0x0) {
    iVar4 = 0;
  }
  else {
    iVar4 = *piVar5;
  }
  while (iVar4 != 0) {
    if ((*(int *)(iVar4 + 0xc) == 0) && (*(float *)(iVar4 + 8) < DAT_00672fd0)) {
      CMonitor__PlayRandomSampleFromChain(&DAT_00896988,*(void **)((int)param_1 + 0x5bc),param_1);
      *(undefined4 *)(iVar4 + 0xc) = 1;
    }
    piVar5 = *(int **)(*(int *)((int)param_1 + 0x29c) + 4);
    *(int **)((int)param_1 + 0x29c) = piVar5;
    if (piVar5 == (int *)0x0) {
      iVar4 = 0;
    }
    else {
      iVar4 = *piVar5;
    }
  }
  if (*(int *)((int)param_1 + 0x4e0) == 0) {
    if ((*(int *)((int)param_1 + 0x4c8) == 0) ||
       (iVar4 = CBattleEngine__IsWeaponModeCompatibleWithMountState
                          (param_1,*(int *)(*(int *)((int)param_1 + 0x4c8) + 0x138),unaff_EDI),
       iVar4 == 0)) {
      to_read = (void *)0x0;
    }
    else {
      if ((*(int *)((int)param_1 + 0x5e8) != 0) || (*(int *)((int)param_1 + 0x4c8) == 0))
      goto LAB_00409d06;
      CMonitor__PlayRandomSampleFromChain(&DAT_00896988,*(void **)((int)param_1 + 0x5c0),param_1);
      to_read = *(void **)((int)param_1 + 0x4c8);
    }
  }
  else {
    if (*(int *)((int)param_1 + 0x5e8) != 0) goto LAB_00409d06;
    CMonitor__PlayRandomSampleFromChain(&DAT_00896988,*(void **)((int)param_1 + 0x5c0),param_1);
    to_read = *(void **)((int)param_1 + 0x4e0);
  }
  CGenericActiveReader__SetReader((void *)((int)param_1 + 0x5e8),to_read);
LAB_00409d06:
  iVar4 = (**(code **)(*(int *)param_1 + 0x10c))();
  fVar3 = _DAT_005d8bd8;
  if ((iVar4 != 0) && (*(int *)((int)param_1 + 0x260) == 2)) {
    fVar1 = SQRT(*(float *)((int)param_1 + 0x84) * *(float *)((int)param_1 + 0x84) +
                 *(float *)((int)param_1 + 0x80) * *(float *)((int)param_1 + 0x80) +
                 *(float *)((int)param_1 + 0x7c) * *(float *)((int)param_1 + 0x7c));
    fVar2 = fVar1 + *(float *)((int)param_1 + 0x5cc);
    *(float *)((int)param_1 + 0x5cc) = fVar2;
    if (fVar3 < fVar2) {
      fVar2 = fVar2 - _DAT_005d8bd8;
      *(int *)((int)param_1 + 0x5d0) = *(int *)((int)param_1 + 0x5d0) + 1;
      *(float *)((int)param_1 + 0x5cc) = fVar2;
    }
    if (_DAT_005d8574 <= fVar1) {
      return;
    }
    if (5 < *(int *)((int)param_1 + 0x5d0)) {
      CMonitor__PlayRandomSampleFromChain(&DAT_00896988,*(void **)((int)param_1 + 0x5c8),param_1);
    }
  }
  *(undefined4 *)((int)param_1 + 0x5d0) = 0;
  return;
}
