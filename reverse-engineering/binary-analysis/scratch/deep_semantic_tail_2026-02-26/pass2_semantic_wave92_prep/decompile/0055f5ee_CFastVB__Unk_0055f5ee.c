/* address: 0x0055f5ee */
/* name: CFastVB__Unk_0055f5ee */
/* signature: int __cdecl CFastVB__Unk_0055f5ee(int param_1, void * param_2) */


int __cdecl CFastVB__Unk_0055f5ee(int param_1,void *param_2)

{
  HANDLE pvVar1;
  DWORD DVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  _WIN32_FIND_DATAA local_144;

  pvVar1 = FindFirstFileA((LPCSTR)param_1,&local_144);
  if (pvVar1 != (HANDLE)0xffffffff) {
    *(uint *)param_2 = -(uint)(local_144.dwFileAttributes != 0x80) & local_144.dwFileAttributes;
    uVar4 = ___timet_from_ft(&local_144.ftCreationTime);
    *(undefined4 *)((int)param_2 + 4) = uVar4;
    uVar4 = ___timet_from_ft(&local_144.ftLastAccessTime);
    *(undefined4 *)((int)param_2 + 8) = uVar4;
    uVar4 = ___timet_from_ft(&local_144.ftLastWriteTime);
    *(undefined4 *)((int)param_2 + 0xc) = uVar4;
    *(DWORD *)((int)param_2 + 0x10) = local_144.nFileSizeLow;
    CDXTexture__Helper_00567de0((void *)((int)param_2 + 0x14),local_144.cFileName);
    return (int)pvVar1;
  }
  DVar2 = GetLastError();
  if (DVar2 < 2) {
LAB_0055f62c:
    puVar3 = (undefined4 *)CTexture__Helper_00567aa8();
    *puVar3 = 0x16;
  }
  else {
    if (3 < DVar2) {
      if (DVar2 == 8) {
        puVar3 = (undefined4 *)CTexture__Helper_00567aa8();
        *puVar3 = 0xc;
        return -1;
      }
      if (DVar2 != 0x12) goto LAB_0055f62c;
    }
    puVar3 = (undefined4 *)CTexture__Helper_00567aa8();
    *puVar3 = 2;
  }
  return -1;
}
