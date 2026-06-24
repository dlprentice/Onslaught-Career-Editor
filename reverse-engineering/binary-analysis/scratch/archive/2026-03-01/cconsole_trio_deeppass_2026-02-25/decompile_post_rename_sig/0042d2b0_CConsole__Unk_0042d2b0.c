/* address: 0x0042d2b0 */
/* name: CConsole__Unk_0042d2b0 */
/* signature: int CConsole__Unk_0042d2b0(void * this, int active, int entry_id, int slot0_device_code, short slot0_scan, int slot1_device_code, short slot1_scan, short slot0_vk, short slot1_vk) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CConsole__Unk_0042d2b0
              (void *this,int active,int entry_id,int slot0_device_code,short slot0_scan,
              int slot1_device_code,short slot1_scan,short slot0_vk,short slot1_vk)

{
  undefined1 *in_ECX;
  undefined2 in_stack_00000016;

  *(int *)(in_ECX + 4) = active;
  *in_ECX = this._0_1_;
  *(int *)(in_ECX + 0xc) = entry_id;
  *(undefined4 *)(in_ECX + 8) = 0;
  *(undefined2 *)(in_ECX + 0x10) = (undefined2)slot0_device_code;
  *(undefined4 *)(in_ECX + 0x14) = 0;
  *(short *)(in_ECX + 0x12) = slot1_scan;
  *(undefined4 *)(in_ECX + 0x18) = _slot0_scan;
  *(undefined2 *)(in_ECX + 0x1c) = (undefined2)slot1_device_code;
  *(short *)(in_ECX + 0x1e) = slot0_vk;
  return (int)in_ECX;
}
