/* address: 0x00595079 */
/* name: CDXTexture__Helper_00595079 */
/* signature: void __stdcall CDXTexture__Helper_00595079(void * param_1, int param_2, int param_3) */


void CDXTexture__Helper_00595079(void *param_1,int param_2,int param_3)

{
  if (*(code **)((int)param_1 + 0x50) == (code *)0x0) {
    CDXTexture__Helper_00592d45(param_1,0x5eeb38);
  }
  else {
    (**(code **)((int)param_1 + 0x50))(param_1,param_2,param_3);
  }
  return;
}
