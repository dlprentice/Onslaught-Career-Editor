/* address: 0x0056a936 */
/* name: CTexture__Helper_0056a936 */
/* signature: char * __cdecl CTexture__Helper_0056a936(int param_1, int param_2, void * param_3, int param_4) */


char * __cdecl CTexture__Helper_0056a936(int param_1,int param_2,void *param_3,int param_4)

{
  undefined4 *puVar1;
  byte bVar2;
  char *pcVar3;
  undefined4 *puVar5;
  BOOL BVar6;
  DWORD DVar7;
  uint uVar8;
  uint *puVar9;
  int iVar10;
  uint uVar11;
  _STARTUPINFOA local_64;
  _PROCESS_INFORMATION local_20;
  LPSTR local_10;
  DWORD local_c;
  char local_5;
  char *pcVar4;

  local_5 = '\0';
  local_c = 0;
  if ((param_1 != 0) && (param_1 != 1)) {
    if (param_1 < 2) {
LAB_0056a986:
      puVar5 = (undefined4 *)CTexture__Helper_00567aa8();
      *puVar5 = 0x16;
      puVar5 = (undefined4 *)CTexture__Helper_00567ab1();
      *puVar5 = 0;
      return (char *)0xffffffff;
    }
    if (3 < param_1) {
      if (param_1 != 4) goto LAB_0056a986;
      local_5 = '\x01';
    }
  }
  local_10 = param_3;
  pcVar3 = param_3;
  while (*pcVar3 != '\0') {
    do {
      pcVar4 = pcVar3;
      pcVar3 = pcVar4 + 1;
    } while (*pcVar3 != '\0');
    if (pcVar4[2] != '\0') {
      *pcVar3 = ' ';
      pcVar3 = pcVar4 + 2;
    }
  }
  _memset(&local_64,0,0x44);
  local_64.cb = 0x44;
  uVar11 = DAT_009d33a0;
  uVar8 = DAT_009d33a0;
  while ((uVar11 != 0 &&
         (uVar8 = uVar8 - 1,
         *(char *)((&DAT_009d32a0)[(int)uVar8 >> 5] + 4 + (uVar8 & 0x1f) * 0x24) == '\0'))) {
    uVar11 = uVar11 - 1;
  }
  uVar8 = uVar11 * 5 + 4;
  local_64.cbReserved2 = (WORD)uVar8;
  local_64.lpReserved2 = (LPBYTE)CTexture__Helper_005689b8(uVar8 & 0xffff,1);
  *(uint *)local_64.lpReserved2 = uVar11;
  uVar8 = 0;
  puVar9 = (uint *)((int)local_64.lpReserved2 + 4);
  puVar5 = (undefined4 *)((int)local_64.lpReserved2 + uVar11 + 4);
  if (0 < (int)uVar11) {
    do {
      puVar1 = (undefined4 *)((&DAT_009d32a0)[(int)uVar8 >> 5] + (uVar8 & 0x1f) * 0x24);
      bVar2 = *(byte *)(puVar1 + 1);
      if ((bVar2 & 0x10) == 0) {
        *(byte *)puVar9 = bVar2;
        *puVar5 = *puVar1;
      }
      else {
        *(byte *)puVar9 = 0;
        *puVar5 = 0xffffffff;
      }
      uVar8 = uVar8 + 1;
      puVar9 = (uint *)((int)puVar9 + 1);
      puVar5 = puVar5 + 1;
    } while ((int)uVar8 < (int)uVar11);
  }
  if (local_5 != '\0') {
    puVar9 = (uint *)((int)local_64.lpReserved2 + 4);
    iVar10 = 0;
    puVar5 = (undefined4 *)((int)local_64.lpReserved2 + uVar11 + 4);
    while( true ) {
      uVar8 = uVar11;
      if (2 < (int)uVar11) {
        uVar8 = 3;
      }
      if ((int)uVar8 <= iVar10) break;
      *(undefined1 *)puVar9 = 0;
      *puVar5 = 0xffffffff;
      iVar10 = iVar10 + 1;
      puVar9 = (uint *)((int)puVar9 + 1);
      puVar5 = puVar5 + 1;
    }
    local_c = 8;
  }
  puVar5 = (undefined4 *)CTexture__Helper_00567aa8();
  *puVar5 = 0;
  puVar5 = (undefined4 *)CTexture__Helper_00567ab1();
  *puVar5 = 0;
  BVar6 = CreateProcessA((LPCSTR)param_2,local_10,(LPSECURITY_ATTRIBUTES)0x0,
                         (LPSECURITY_ATTRIBUTES)0x0,1,local_c,(LPVOID)param_4,(LPCSTR)0x0,&local_64,
                         &local_20);
  DVar7 = GetLastError();
  CRT__FreeBase((int)local_64.lpReserved2);
  if (BVar6 == 0) {
    CTexture__Helper_00567a35(DVar7);
    return (char *)0xffffffff;
  }
  if (param_1 == 2) {
                    /* WARNING: Subroutine does not return */
    __exit(0);
  }
  if (param_1 == 0) {
    WaitForSingleObject(local_20.hProcess,0xffffffff);
    GetExitCodeProcess(local_20.hProcess,(LPDWORD)&param_3);
    CloseHandle(local_20.hProcess);
  }
  else if (param_1 == 4) {
    CloseHandle(local_20.hProcess);
    param_3 = (void *)0x0;
  }
  else {
    param_3 = local_20.hProcess;
  }
  CloseHandle(local_20.hThread);
  return param_3;
}
