/* address: 0x0056e8d5 */
/* name: CRT__PutEnvStringAndUpdateProcessEnv */
/* signature: int __cdecl CRT__PutEnvStringAndUpdateProcessEnv(void * param_1, int param_2) */


int __cdecl CRT__PutEnvStringAndUpdateProcessEnv(void *param_1,int param_2)

{
  void *pvVar1;
  int iVar2;
  int *piVar3;
  size_t sVar4;
  LPCSTR lpName;
  undefined1 *puVar5;
  int *piVar6;
  bool bVar7;

  if (param_1 == (void *)0x0) {
    return -1;
  }
  pvVar1 = (void *)CRT__MbsChr(param_1,0x3d);
  if (pvVar1 == (void *)0x0) {
    return -1;
  }
  if (param_1 == pvVar1) {
    return -1;
  }
  bVar7 = *(char *)((int)pvVar1 + 1) == '\0';
  if (DAT_009d08dc == DAT_009d08e0) {
    DAT_009d08dc = (int *)CRT__CloneEnvironmentTable(DAT_009d08dc);
  }
  if (DAT_009d08dc == (int *)0x0) {
    if ((param_2 == 0) || (DAT_009d08e4 == (undefined4 *)0x0)) {
      if (bVar7) {
        return 0;
      }
      DAT_009d08dc = _malloc(4);
      if (DAT_009d08dc == (int *)0x0) {
        return -1;
      }
      *DAT_009d08dc = 0;
      if (DAT_009d08e4 == (undefined4 *)0x0) {
        DAT_009d08e4 = _malloc(4);
        if (DAT_009d08e4 == (undefined4 *)0x0) {
          return -1;
        }
        *DAT_009d08e4 = 0;
      }
    }
    else {
      iVar2 = CRT__ProcessWideArgvTableToMultibyte();
      if (iVar2 != 0) {
        return -1;
      }
    }
  }
  piVar3 = DAT_009d08dc;
  iVar2 = CRT__FindEnvVarIndexOrInsertionPoint(param_1,(int)pvVar1 - (int)param_1);
  if ((iVar2 < 0) || (*piVar3 == 0)) {
    if (bVar7) {
      return 0;
    }
    if (iVar2 < 0) {
      iVar2 = -iVar2;
    }
    piVar3 = (int *)CRT__ReallocBase(piVar3,iVar2 * 4 + 8);
    if (piVar3 == (int *)0x0) {
      return -1;
    }
    piVar3[iVar2] = (int)param_1;
    piVar3[iVar2 + 1] = 0;
  }
  else {
    if (!bVar7) {
      piVar3[iVar2] = (int)param_1;
      goto LAB_0056ea09;
    }
    piVar6 = piVar3 + iVar2;
    CRT__FreeBase(piVar3[iVar2]);
    for (; *piVar6 != 0; piVar6 = piVar6 + 1) {
      iVar2 = iVar2 + 1;
      *piVar6 = piVar6[1];
    }
    piVar3 = (int *)CRT__ReallocBase(piVar3,iVar2 << 2);
    if (piVar3 == (int *)0x0) goto LAB_0056ea09;
  }
  DAT_009d08dc = piVar3;
LAB_0056ea09:
  if (param_2 != 0) {
    sVar4 = _strlen(param_1);
    lpName = _malloc(sVar4 + 2);
    if (lpName != (LPCSTR)0x0) {
      CRT__StrCpyAligned(lpName,param_1);
      puVar5 = (undefined1 *)(((int)lpName - (int)param_1) + (int)pvVar1);
      *puVar5 = 0;
      SetEnvironmentVariableA(lpName,(LPCSTR)(~-(uint)bVar7 & (uint)(puVar5 + 1)));
      CRT__FreeBase((int)lpName);
    }
  }
  return 0;
}
