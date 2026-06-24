/* address: 0x005b25e0 */
/* name: CDXTexture__CloseAsyncDecodeHandles */
/* signature: int __stdcall CDXTexture__CloseAsyncDecodeHandles(void * param_1, int param_2) */


int CDXTexture__CloseAsyncDecodeHandles(void *param_1,int param_2)

{
  CDXTexture__Helper_005b1db0(param_1,param_2,(void *)0x0);
  (**(code **)(param_2 + 0x24))
            (*(undefined4 *)(param_2 + 0x28),*(undefined4 *)((int)param_1 + 0x28));
  (**(code **)(param_2 + 0x24))
            (*(undefined4 *)(param_2 + 0x28),*(undefined4 *)((int)param_1 + 0x24));
  (**(code **)(param_2 + 0x24))(*(undefined4 *)(param_2 + 0x28),param_1);
  return 0;
}
