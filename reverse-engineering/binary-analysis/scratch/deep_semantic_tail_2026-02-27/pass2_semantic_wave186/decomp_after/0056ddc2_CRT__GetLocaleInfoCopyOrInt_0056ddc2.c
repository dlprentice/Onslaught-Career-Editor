/* address: 0x0056ddc2 */
/* name: CRT__GetLocaleInfoCopyOrInt_0056ddc2 */
/* signature: int __cdecl CRT__GetLocaleInfoCopyOrInt_0056ddc2(int param_1, int param_2, int param_3, void * param_4) */


int __cdecl CRT__GetLocaleInfoCopyOrInt_0056ddc2(int param_1,int param_2,int param_3,void *param_4)

{
  byte bVar1;
  bool bVar2;
  size_t sVar3;
  DWORD DVar4;
  char *_Source;
  char *_Dest;
  int iVar5;
  uint uVar6;
  void *extraout_ECX;
  undefined *puVar7;
  void *this;
  byte *pbVar8;
  uint unaff_EDI;
  char local_84 [128];

  if (param_1 != 1) {
    if (param_1 != 0) {
      return -1;
    }
    pbVar8 = &DAT_009d0c20;
    iVar5 = CRT__GetLocaleInfoAsWide(param_2,param_3,0x9d0c20,4,0);
    if (iVar5 != 0) {
      *(undefined1 *)param_4 = 0;
      this = extraout_ECX;
      while( true ) {
        bVar1 = *pbVar8;
        if (DAT_00653a9c < 2) {
          uVar6 = (byte)PTR_DAT_00653890[(uint)bVar1 * 2] & 4;
          puVar7 = PTR_DAT_00653890;
        }
        else {
          puVar7 = (undefined *)0x0;
          uVar6 = CRT__GetCharTypeMask_Compat(this,(uint)bVar1,4,unaff_EDI);
        }
        if (uVar6 == 0) break;
        this = (void *)CONCAT31((int3)((uint)puVar7 >> 8),10);
        pbVar8 = pbVar8 + 2;
        *(byte *)param_4 = *(char *)param_4 * '\n' + bVar1 + -0x30;
        if (0x9d0c27 < (int)pbVar8) {
          return 0;
        }
      }
      return 0;
    }
    return -1;
  }
  _Source = local_84;
  bVar2 = false;
  sVar3 = CRT__GetLocaleInfoAsMultiByte(param_2,param_3,(int)local_84,0x80,0);
  if (sVar3 == 0) {
    DVar4 = GetLastError();
    if (DVar4 != 0x7a) {
      return -1;
    }
    sVar3 = CRT__GetLocaleInfoAsMultiByte(param_2,param_3,0,0,0);
    if (sVar3 == 0) {
      return -1;
    }
    _Source = _malloc(sVar3);
    if (_Source == (char *)0x0) {
      return -1;
    }
    bVar2 = true;
    sVar3 = CRT__GetLocaleInfoAsMultiByte(param_2,param_3,(int)_Source,sVar3,0);
    if (sVar3 == 0) goto LAB_0056de60;
  }
  _Dest = _malloc(sVar3);
  *(char **)param_4 = _Dest;
  if (_Dest != (char *)0x0) {
    _strncpy(_Dest,_Source,sVar3);
    if (bVar2) {
      CRT__FreeBase((int)_Source);
    }
    return 0;
  }
  if (!bVar2) {
    return -1;
  }
LAB_0056de60:
  CRT__FreeBase((int)_Source);
  return -1;
}
