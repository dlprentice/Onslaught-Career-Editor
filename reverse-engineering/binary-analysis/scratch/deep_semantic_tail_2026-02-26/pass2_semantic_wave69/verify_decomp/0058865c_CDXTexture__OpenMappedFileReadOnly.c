/* address: 0x0058865c */
/* name: CDXTexture__OpenMappedFileReadOnly */
/* signature: int __thiscall CDXTexture__OpenMappedFileReadOnly(void * this, void * param_1, int param_2, int param_3) */


int __thiscall CDXTexture__OpenMappedFileReadOnly(void *this,void *param_1,int param_2,int param_3)

{
  HANDLE pvVar1;
  DWORD DVar2;
  LPVOID pvVar3;
  _OSVERSIONINFOA local_9c;
  int local_8;

  if (param_1 == (void *)0x0) {
    return -0x7789f794;
  }
  if (param_2 == 0) {
LAB_005886ff:
    pvVar1 = CreateFileA(param_1,0x80000000,1,(LPSECURITY_ATTRIBUTES)0x0,3,0x10000000,(HANDLE)0x0);
  }
  else {
    local_9c.dwOSVersionInfoSize = 0x94;
    GetVersionExA(&local_9c);
    if (local_9c.dwPlatformId != 2) {
      local_8 = WideCharToMultiByte(0xfde9,0,param_1,-1,(LPSTR)0x0,0,(LPCSTR)0x0,(LPBOOL)0x0);
      CDXTexture__Helper_0055def0();
      WideCharToMultiByte(0xfde9,0,param_1,-1,&stack0xffffff58,local_8,(LPCSTR)0x0,(LPBOOL)0x0);
      param_2 = 0;
      param_1 = &stack0xffffff58;
    }
    if (param_2 == 0) goto LAB_005886ff;
    pvVar1 = CreateFileW(param_1,0x80000000,1,(LPSECURITY_ATTRIBUTES)0x0,3,0x10000000,(HANDLE)0x0);
  }
  *(HANDLE *)this = pvVar1;
  if (pvVar1 != (HANDLE)0xffffffff) {
    pvVar1 = CreateFileMappingA(pvVar1,(LPSECURITY_ATTRIBUTES)0x0,2,0,0,(LPCSTR)0x0);
    *(HANDLE *)((int)this + 4) = pvVar1;
    if (pvVar1 != (HANDLE)0xffffffff) {
      DVar2 = GetFileSize(*(HANDLE *)this,(LPDWORD)0x0);
      *(DWORD *)((int)this + 0xc) = DVar2;
      if (DVar2 != 0xffffffff) {
        if (DVar2 == 0) {
          *(undefined4 *)((int)this + 8) = 0;
        }
        else {
          pvVar3 = MapViewOfFile(*(HANDLE *)((int)this + 4),4,0,0,0);
          *(LPVOID *)((int)this + 8) = pvVar3;
          if (pvVar3 == (LPVOID)0x0) goto LAB_0058875e;
        }
        return 0;
      }
    }
  }
LAB_0058875e:
  GetLastError();
  return -0x7789f4a7;
}
