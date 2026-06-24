/* address: 0x005027f0 */
/* name: CVertexShader__LoadCompiledShaderBlobFromVSOFile */
/* signature: int CVertexShader__LoadCompiledShaderBlobFromVSOFile(void) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CVertexShader__LoadCompiledShaderBlobFromVSOFile(void)

{
  LPCSTR lpFileName;
  HANDLE hHeap;
  LPVOID lpBuffer;
  int extraout_EAX;
  int iVar1;
  DWORD DVar2;
  DWORD DVar3;
  LPSECURITY_ATTRIBUTES lpSecurityAttributes;
  DWORD dwCreationDisposition;
  DWORD dwFlagsAndAttributes;
  HANDLE pvVar4;
  DWORD DStack_204;
  char local_200 [256];
  char acStack_100 [256];

  sprintf(local_200,s___Shaders__s_vso_0063d090);
  pvVar4 = (HANDLE)0x0;
  dwFlagsAndAttributes = 0;
  dwCreationDisposition = 3;
  lpSecurityAttributes = (LPSECURITY_ATTRIBUTES)0x0;
  DVar3 = 0;
  DVar2 = 0x80000000;
  lpFileName = (LPCSTR)CD3DApplication__Helper_004f7c70(local_200);
  pvVar4 = CreateFileA(lpFileName,DVar2,DVar3,lpSecurityAttributes,dwCreationDisposition,
                       dwFlagsAndAttributes,pvVar4);
  if (pvVar4 == (HANDLE)0xffffffff) {
    sprintf(acStack_100,s_Could_not_find_shader_file__s_0063d070);
    return -0x7fffbffb;
  }
  DVar2 = GetFileSize(pvVar4,(LPDWORD)0x0);
  DVar3 = 8;
  DStack_204 = DVar2;
  hHeap = GetProcessHeap();
  lpBuffer = HeapAlloc(hHeap,DVar3,DVar2);
  if (lpBuffer == (LPVOID)0x0) {
    sprintf(acStack_100,s_Failed_to_allocate_memory_for_sh_0063d048);
    return -0x7fffbffb;
  }
  ReadFile(pvVar4,lpBuffer,DStack_204,&DStack_204,(LPOVERLAPPED)0x0);
  CloseHandle(pvVar4);
  CEngine__DeviceCall16C_Arg2Arg3(&DAT_00855bb0,0,(int)lpBuffer);
  if (extraout_EAX < 0) {
    DebugTrace(s_Could_not_create_shader_from_cod_0063cf3c);
    iVar1 = extraout_EAX;
  }
  else {
    iVar1 = 0;
  }
  DVar2 = 0;
  pvVar4 = GetProcessHeap();
  HeapFree(pvVar4,DVar2,lpBuffer);
  return iVar1;
}
