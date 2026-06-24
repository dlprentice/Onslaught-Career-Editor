/* address: 0x004d06e0 */
/* name: CPauseMenu__ResumeGameAndPersistOptions */
/* signature: void __fastcall CPauseMenu__ResumeGameAndPersistOptions(void * param_1) */


void __fastcall CPauseMenu__ResumeGameAndPersistOptions(void *param_1)

{
  void *pvVar1;
  int iVar2;
  int iVar3;
  float fVar4;
  void *local_4;

  local_4 = param_1;
  if (DAT_0082b4e8 == '\0') {
    iVar3 = 0;
    do {
      pvVar1 = CGame__GetController(&DAT_008a9a98,iVar3);
      if (pvVar1 != (void *)0x0) {
        pvVar1 = CGame__GetController(&DAT_008a9a98,iVar3);
        pvVar1 = CController__GetToControl(pvVar1);
        if (pvVar1 == param_1) {
          pvVar1 = CGame__GetController(&DAT_008a9a98,iVar3);
          CController__RelinquishControl(pvVar1);
        }
      }
      iVar3 = iVar3 + 1;
    } while (iVar3 < 2);
    CGame__UnPause(&DAT_008a9a98);
    PlatformInput__InitMouse();
    iVar3 = CCareer__GetSaveSize();
    pvVar1 = (void *)OID__AllocObject(iVar3,0x61,s_C__dev_ONSLAUGHT2_PauseMenu_cpp_006314dc,0x60b);
    CCareer__Save(&CAREER,pvVar1);
    if (DAT_008a1388 != 0) {
      iVar2 = EnumerateSaveFiles_Main(DAT_008a9694,&DAT_008a1388,(int *)&local_4,1);
      if (iVar2 == 0) {
        PCPlatform__WriteSaveFile(DAT_008a9694,(int)local_4,&DAT_008a1388,pvVar1,iVar3);
      }
    }
    CFEPOptions__WriteDefaultOptionsFile(pvVar1,iVar3);
    OID__FreeObject(pvVar1);
  }
  *(undefined4 *)((int)param_1 + 0x10) = 0;
  fVar4 = PLATFORM__GetSysTimeFloat();
  *(float *)((int)param_1 + 0x30) = fVar4;
  if (*(int **)((int)param_1 + 8) != (int *)0x0) {
    (**(code **)(**(int **)((int)param_1 + 8) + 4))(1);
    *(undefined4 *)((int)param_1 + 8) = 0;
  }
  if (*(int **)((int)param_1 + 0x3c) != (int *)0x0) {
    (**(code **)(**(int **)((int)param_1 + 0x3c) + 4))(1);
    *(undefined4 *)((int)param_1 + 0x3c) = 0;
  }
  *(undefined4 *)((int)param_1 + 0x48) = 0;
  return;
}
