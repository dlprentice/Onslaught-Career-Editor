/* address: 0x005282b0 */
/* name: PCPlatform__InitAsyncMusicStream */
/* signature: void PCPlatform__InitAsyncMusicStream(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

void PCPlatform__InitAsyncMusicStream(void)

{
  void *pvVar1;
  undefined4 extraout_EAX;
  int iVar2;
  undefined4 *puVar3;
  int *piVar4;
  undefined1 *puStack_70;
  undefined4 local_44;
  undefined4 local_40;
  undefined4 local_3c;
  undefined4 local_38;
  undefined2 local_34;
  undefined4 local_30 [4];
  undefined4 *local_20;
  void *local_c;
  undefined1 *puStack_8;
  undefined4 uStack_4;

  uStack_4 = 0xffffffff;
  puStack_8 = &LAB_005d692b;
  local_c = ExceptionList;
  puVar3 = local_30;
  for (iVar2 = 9; iVar2 != 0; iVar2 = iVar2 + -1) {
    *puVar3 = 0;
    puVar3 = puVar3 + 1;
  }
  local_20 = &local_44;
  local_44 = 0x20001;
  local_40 = 0xac44;
  local_38 = 0x100004;
  local_3c = 0x2b110;
  local_34 = 0;
  local_30[0] = 0x24;
  local_30[2] = 0x80000;
  local_30[1] = 0x188;
  if (DAT_00896a48 != (int *)0x0) {
    puStack_70 = (undefined1 *)0x0;
    ExceptionList = &local_c;
    piVar4 = DAT_00896a48;
    (**(code **)(*DAT_00896a48 + 0xc))(DAT_00896a48,local_30,&DAT_0089bec8);
    DAT_0089bec4 = CreateEventA((LPSECURITY_ATTRIBUTES)0x0,0,0,(LPCSTR)0x0);
    DAT_0089bec0 = CreateEventA((LPSECURITY_ATTRIBUTES)0x0,0,0,(LPCSTR)0x0);
    DAT_0089bebc = CreateEventA((LPSECURITY_ATTRIBUTES)0x0,0,0,(LPCSTR)0x0);
    DAT_0089beb8 = CreateEventA((LPSECURITY_ATTRIBUTES)0x0,0,0,(LPCSTR)0x0);
    DAT_0089beb4 = CreateThread((LPSECURITY_ATTRIBUTES)0x0,0,PCPlatform__AsyncMusicStreamWorkerMain,
                                (LPVOID)0x0,0,(LPDWORD)&stack0xffffff94);
    puStack_70 = (undefined1 *)0x0;
    iVar2 = (**(code **)*DAT_0089bec8)(DAT_0089bec8,&DAT_0060c08c,&puStack_70);
    if (-1 < iVar2) {
      puStack_70 = (undefined1 *)0x40000;
      (**(code **)(*piVar4 + 0xc))(piVar4,2,&puStack_70);
    }
    (**(code **)(*piVar4 + 8))(piVar4);
    puStack_70 = &DAT_00662b2c;
    pvVar1 = (void *)OID__AllocObject(0x22f0,0);
    uStack_4 = 0;
    if (pvVar1 == (void *)0x0) {
      DAT_0089bfd4 = 0;
    }
    else {
      COggFileRead__ctor_like_005245a0(pvVar1);
      DAT_0089bfd4 = extraout_EAX;
    }
    puVar3 = &DAT_0089bed4;
    for (iVar2 = 0x40; iVar2 != 0; iVar2 = iVar2 + -1) {
      *puVar3 = 0;
      puVar3 = puVar3 + 1;
    }
    DAT_0089bed0 = 0;
  }
  ExceptionList = local_c;
  return;
}
