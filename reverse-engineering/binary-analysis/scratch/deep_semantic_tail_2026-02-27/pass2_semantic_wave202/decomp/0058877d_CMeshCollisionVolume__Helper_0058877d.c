/* address: 0x0058877d */
/* name: CMeshCollisionVolume__Helper_0058877d */
/* signature: int __thiscall CMeshCollisionVolume__Helper_0058877d(void * this, void * param_1, int param_2, int param_3) */


int __thiscall
CMeshCollisionVolume__Helper_0058877d(void *this,void *param_1,int param_2,int param_3)

{
  HANDLE pvVar1;
  int iVar2;
  _OSVERSIONINFOA local_a0;
  int local_c;
  undefined4 *local_8;

  if (param_1 == (void *)0x0) {
    return -0x7789f794;
  }
  local_8 = this;
  if (param_2 != 0) {
    local_a0.dwOSVersionInfoSize = 0x94;
    GetVersionExA(&local_a0);
    if (local_a0.dwPlatformId != 2) {
      local_c = WideCharToMultiByte(0xfde9,0,param_1,-1,(LPSTR)0x0,0,(LPCSTR)0x0,(LPBOOL)0x0);
      CRT__AllocaProbe();
      WideCharToMultiByte(0xfde9,0,param_1,-1,&stack0xffffff54,local_c,(LPCSTR)0x0,(LPBOOL)0x0);
      param_2 = 0;
      this = local_8;
      param_1 = &stack0xffffff54;
    }
    if (param_2 != 0) {
      pvVar1 = CreateFileW(param_1,0x40000000,0,(LPSECURITY_ATTRIBUTES)0x0,2,0,(HANDLE)0x0);
      goto LAB_00588832;
    }
  }
  pvVar1 = CreateFileA(param_1,0x40000000,0,(LPSECURITY_ATTRIBUTES)0x0,2,0,(HANDLE)0x0);
LAB_00588832:
  *(HANDLE *)this = pvVar1;
  if (pvVar1 == (HANDLE)0xffffffff) {
    GetLastError();
    iVar2 = -0x7789f4a7;
  }
  else {
    iVar2 = 0;
  }
  return iVar2;
}
