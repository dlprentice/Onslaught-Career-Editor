/* address: 0x005935d9 */
/* name: CDXTexture__GetOutputChannelCount */
/* signature: int __stdcall CDXTexture__GetOutputChannelCount(int param_1, int param_2) */


int CDXTexture__GetOutputChannelCount(int param_1,int param_2)

{
  uint in_EAX;
  uint uVar1;

  if ((param_1 == 0) || (in_EAX = 0, param_2 == 0)) {
    uVar1 = in_EAX & 0xffffff00;
  }
  else {
    uVar1 = CONCAT31((int3)((uint)param_2 >> 8),*(undefined1 *)(param_2 + 0x1d));
  }
  return uVar1;
}
