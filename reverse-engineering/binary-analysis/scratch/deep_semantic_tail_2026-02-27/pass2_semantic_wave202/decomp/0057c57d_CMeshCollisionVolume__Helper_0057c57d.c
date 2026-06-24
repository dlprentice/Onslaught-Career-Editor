/* address: 0x0057c57d */
/* name: CMeshCollisionVolume__Helper_0057c57d */
/* signature: int __stdcall CMeshCollisionVolume__Helper_0057c57d(int param_1) */


int CMeshCollisionVolume__Helper_0057c57d(int param_1)

{
  undefined4 *puVar1;

  puVar1 = *(undefined4 **)(param_1 + 0x18);
  WriteFile((HANDLE)puVar1[5],(LPCVOID)puVar1[6],0x1000,(LPDWORD)&param_1,(LPOVERLAPPED)0x0);
  *puVar1 = puVar1[6];
  puVar1[1] = 0x1000;
  return 1;
}
