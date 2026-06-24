/* address: 0x0056586a */
/* name: CRT__SetLocale */
/* signature: int __cdecl CRT__SetLocale(int param_1, void * param_2) */


int __cdecl CRT__SetLocale(int param_1,void *param_2)

{
  int iVar1;
  char *pcVar2;
  size_t sVar3;
  int iVar4;
  int iVar5;
  undefined **ppuVar6;
  char *_Str2;
  undefined4 *puVar7;
  char local_8c [132];
  size_t local_8;

  iVar5 = 0;
  if ((param_1 < 0) || (5 < param_1)) {
    return 0;
  }
  CDXTexture__Helper_00561179(0x13);
  DAT_009d35ec = DAT_009d35ec + 1;
  while (DAT_009d35f0 != 0) {
    Sleep(1);
  }
  if (param_1 == 0) {
    local_8 = 1;
    param_1 = 0;
    if (param_2 == (void *)0x0) {
LAB_00565a90:
      iVar1 = CRT__BuildCompositeLocaleString();
    }
    else {
      if (((*(char *)param_2 == 'L') && (*(char *)((int)param_2 + 1) == 'C')) &&
         (*(char *)((int)param_2 + 2) == '_')) {
        pcVar2 = (char *)CTexture__Helper_0056c0a0(param_2,&DAT_005e5e28);
        _Str2 = param_2;
        while (((pcVar2 != (char *)0x0 && (local_8 = (int)pcVar2 - (int)_Str2, local_8 != 0)) &&
               (*pcVar2 != ';'))) {
          param_2 = (void *)0x1;
          ppuVar6 = &PTR_s_LC_COLLATE_00653d3c;
          do {
            iVar5 = _strncmp(*ppuVar6,_Str2,local_8);
            if ((iVar5 == 0) && (sVar3 = _strlen(*ppuVar6), local_8 == sVar3)) break;
            param_2 = (void *)((int)param_2 + 1);
            ppuVar6 = ppuVar6 + 3;
          } while ((int)ppuVar6 < 0x653d6d);
          pcVar2 = pcVar2 + 1;
          sVar3 = CTexture__Helper_0056c060(pcVar2,&DAT_005e5e24);
          if ((sVar3 == 0) && (*pcVar2 != ';')) break;
          if ((int)param_2 < 6) {
            _strncpy(local_8c,pcVar2,sVar3);
            local_8c[sVar3] = '\0';
            iVar5 = CRT__SetLocaleCategory((int)param_2,(int)local_8c);
            if (iVar5 != 0) {
              param_1 = param_1 + 1;
            }
          }
          if ((pcVar2[sVar3] == '\0') || (_Str2 = pcVar2 + sVar3 + 1, *_Str2 == '\0'))
          goto LAB_005659fa;
          pcVar2 = (char *)CTexture__Helper_0056c0a0(_Str2,&DAT_005e5e28);
        }
        CTexture__Helper_005611da(0x13);
        iVar1 = 0;
        goto LAB_00565a9f;
      }
      iVar4 = CRT__ResolveLocaleNameAndMetadata(param_2,local_8c,(void *)0x0,(void *)0x0);
      iVar1 = 0;
      if (iVar4 != 0) {
        puVar7 = &DAT_00653d34;
        do {
          if (puVar7 != &DAT_00653d34) {
            iVar1 = _strcmp(local_8c,(char *)*puVar7);
            if ((iVar1 == 0) || (iVar1 = CRT__SetLocaleCategory(iVar5,(int)local_8c), iVar1 != 0)) {
              param_1 = param_1 + 1;
            }
            else {
              local_8 = 0;
            }
          }
          puVar7 = puVar7 + 3;
          iVar5 = iVar5 + 1;
        } while ((int)puVar7 < 0x653d71);
        if (local_8 == 0) {
LAB_005659fa:
          if (param_1 != 0) goto LAB_00565a90;
          iVar1 = 0;
        }
        else {
          iVar1 = CRT__BuildCompositeLocaleString();
          CRT__FreeBase(DAT_00653d34);
          DAT_00653d34 = 0;
        }
      }
    }
  }
  else if (param_2 == (void *)0x0) {
    iVar1 = (&DAT_00653d34)[param_1 * 3];
  }
  else {
    iVar1 = CRT__SetLocaleCategory(param_1,(int)param_2);
  }
  CTexture__Helper_005611da(0x13);
LAB_00565a9f:
  DAT_009d35ec = DAT_009d35ec + -1;
  return iVar1;
}
