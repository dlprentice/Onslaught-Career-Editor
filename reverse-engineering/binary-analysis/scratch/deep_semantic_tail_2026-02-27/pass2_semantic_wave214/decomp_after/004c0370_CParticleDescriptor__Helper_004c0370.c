/* address: 0x004c0370 */
/* name: CParticleDescriptor__Helper_004c0370 */
/* signature: void __thiscall CParticleDescriptor__Helper_004c0370(void * this, int param_1, void * param_2) */


void __thiscall CParticleDescriptor__Helper_004c0370(void *this,int param_1,void *param_2)

{
  undefined4 *puVar1;

  puVar1 = *(undefined4 **)((int)this + 4);
  if (puVar1 != (undefined4 *)0x0) {
    if (puVar1[0x12] == 0x461c4000) {
      puVar1[0x20] = *(undefined4 *)param_1;
      puVar1[0x21] = *(undefined4 *)(param_1 + 4);
      puVar1[0x22] = *(undefined4 *)(param_1 + 8);
      puVar1[0x23] = *(undefined4 *)(param_1 + 0xc);
      puVar1[0x10] = *(undefined4 *)param_1;
      puVar1[0x11] = *(undefined4 *)(param_1 + 4);
      puVar1[0x12] = *(undefined4 *)(param_1 + 8);
      puVar1[0x13] = *(undefined4 *)(param_1 + 0xc);
      *puVar1 = *(undefined4 *)param_1;
      puVar1[1] = *(undefined4 *)(param_1 + 4);
      puVar1[2] = *(undefined4 *)(param_1 + 8);
      puVar1[3] = *(undefined4 *)(param_1 + 0xc);
      if (puVar1[0x2b] != -0x40800000) {
        puVar1[0x2b] = DAT_00672fd0;
        return;
      }
    }
    else {
      puVar1[0x10] = *puVar1;
      puVar1[0x11] = puVar1[1];
      puVar1[0x12] = puVar1[2];
      puVar1[0x13] = puVar1[3];
      *puVar1 = *(undefined4 *)param_1;
      puVar1[1] = *(undefined4 *)(param_1 + 4);
      puVar1[2] = *(undefined4 *)(param_1 + 8);
      puVar1[3] = *(undefined4 *)(param_1 + 0xc);
      if (puVar1[0x2b] != -0x40800000) {
        puVar1[0x2b] = DAT_00672fd0;
      }
    }
  }
  return;
}
