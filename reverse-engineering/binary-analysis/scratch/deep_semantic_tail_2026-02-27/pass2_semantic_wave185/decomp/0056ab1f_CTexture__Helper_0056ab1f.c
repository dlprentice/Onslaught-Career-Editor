/* address: 0x0056ab1f */
/* name: CTexture__Helper_0056ab1f */
/* signature: int __cdecl CTexture__Helper_0056ab1f(void * param_1, void * param_2, void * param_3, void * param_4) */


int __cdecl CTexture__Helper_0056ab1f(void *param_1,void *param_2,void *param_3,void *param_4)

{
  size_t sVar1;
  void *pvVar2;
  size_t sVar3;
  char *pcVar4;
  void *pvVar5;
  undefined4 *puVar6;
  int iVar7;
  char cVar8;
  size_t sVar9;
  undefined1 *puVar10;
  void *pvVar11;

  sVar9 = 2;
  sVar3 = sVar9;
  for (puVar6 = param_1; (char *)*puVar6 != (char *)0x0; puVar6 = puVar6 + 1) {
    sVar1 = _strlen((char *)*puVar6);
    sVar3 = sVar3 + 1 + sVar1;
  }
  pvVar2 = _malloc(sVar3);
  *(void **)param_3 = pvVar2;
  if (pvVar2 == (void *)0x0) {
    *(undefined4 *)param_4 = 0;
LAB_0056ac40:
    puVar6 = (undefined4 *)CTexture__Helper_00567aa8();
    *puVar6 = 0xc;
    puVar6 = (undefined4 *)CTexture__Helper_00567ab1();
    *puVar6 = 8;
LAB_0056ac56:
    iVar7 = -1;
  }
  else {
    puVar6 = param_2;
    if (param_2 == (void *)0x0) {
      *(undefined4 *)param_4 = 0;
      pvVar2 = param_4;
      pvVar11 = param_4;
    }
    else {
      for (; (char *)*puVar6 != (char *)0x0; puVar6 = puVar6 + 1) {
        sVar3 = _strlen((char *)*puVar6);
        sVar9 = sVar9 + 1 + sVar3;
      }
      if (DAT_009d090c == (char *)0x0) {
        DAT_009d090c = (char *)CTexture__Helper_00569124();
        if (DAT_009d090c != (char *)0x0) goto LAB_0056abbd;
        goto LAB_0056ac56;
      }
LAB_0056abbd:
      pvVar2 = (void *)0x0;
      if (*DAT_009d090c != '\0') {
        cVar8 = *DAT_009d090c;
        pcVar4 = DAT_009d090c;
        do {
          if (cVar8 == '=') break;
          sVar3 = _strlen(pcVar4);
          pvVar2 = (void *)((int)pvVar2 + sVar3 + 1);
          cVar8 = DAT_009d090c[(int)pvVar2];
          pcVar4 = DAT_009d090c + (int)pvVar2;
        } while (cVar8 != '\0');
      }
      pcVar4 = DAT_009d090c + (int)pvVar2;
      pvVar11 = pvVar2;
      while ((((*pcVar4 == '=' && (pcVar4[1] != '\0')) && (pcVar4[2] == ':')) && (pcVar4[3] == '='))
            ) {
        sVar3 = _strlen(pcVar4 + 4);
        pvVar11 = (void *)((int)pvVar11 + sVar3 + 5);
        pcVar4 = DAT_009d090c + (int)pvVar11;
      }
      pvVar5 = _malloc((int)pvVar11 + (sVar9 - (int)pvVar2));
      *(void **)param_4 = pvVar5;
      if (pvVar5 == (void *)0x0) {
        CRT__FreeBase(*(int *)param_3);
        *(undefined4 *)param_3 = 0;
        goto LAB_0056ac40;
      }
    }
    puVar10 = *(undefined1 **)param_3;
    param_3 = param_1;
    if (*(void **)param_1 != (void *)0x0) {
      CRT__StrCpyAligned(puVar10,*(void **)param_1);
      param_3 = (void *)((int)param_1 + 4);
      sVar3 = _strlen(*(char **)param_1);
      puVar10 = puVar10 + sVar3 + 1;
      goto LAB_0056ac7d;
    }
    while( true ) {
      puVar10 = puVar10 + 1;
LAB_0056ac7d:
      if (*(void **)param_3 == (void *)0x0) break;
      CRT__StrCpyAligned(puVar10,*(void **)param_3);
      sVar3 = _strlen(*(char **)param_3);
      puVar10 = puVar10 + sVar3;
      *puVar10 = 0x20;
      param_3 = (void *)((int)param_3 + 4);
    }
    puVar10[-1] = 0;
    *puVar10 = 0;
    puVar10 = *(undefined1 **)param_4;
    if (param_2 != (void *)0x0) {
      CTexture__Helper_00567700(puVar10,DAT_009d090c + (int)pvVar2,(int)pvVar11 - (int)pvVar2);
      puVar10 = puVar10 + ((int)pvVar11 - (int)pvVar2);
      for (; *(void **)param_2 != (void *)0x0; param_2 = (void *)((int)param_2 + 4)) {
        CRT__StrCpyAligned(puVar10,*(void **)param_2);
        sVar3 = _strlen(*(char **)param_2);
        puVar10 = puVar10 + sVar3 + 1;
      }
    }
    if (puVar10 != (undefined1 *)0x0) {
      if (puVar10 == *(undefined1 **)param_4) {
        *puVar10 = 0;
        puVar10 = puVar10 + 1;
      }
      *puVar10 = 0;
    }
    CRT__FreeBase((int)DAT_009d090c);
    DAT_009d090c = (char *)0x0;
    iVar7 = 0;
  }
  return iVar7;
}
