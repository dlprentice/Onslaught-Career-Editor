/* address: 0x0042d260 */
/* name: CConsole__Unk_0042d260 */
/* signature: int CConsole__Unk_0042d260(void * this, int active, int entry_id, int slot0_device_code, short slot0_scan, short slot0_vk) */


/* WARNING: Unknown calling convention -- yet parameter storage is locked */

int CConsole__Unk_0042d260
              (void *this,int active,int entry_id,int slot0_device_code,short slot0_scan,
              short slot0_vk)

{
  undefined1 *in_ECX;

  *(int *)(in_ECX + 4) = active;
  *(int *)(in_ECX + 0xc) = entry_id;
  *in_ECX = this._0_1_;
  *(undefined2 *)(in_ECX + 0x10) = (undefined2)slot0_device_code;
  *(undefined4 *)(in_ECX + 8) = 0;
  *(short *)(in_ECX + 0x12) = slot0_scan;
  *(undefined4 *)(in_ECX + 0x14) = 0xffffffff;
  *(undefined4 *)(in_ECX + 0x18) = 0;
  *(undefined2 *)(in_ECX + 0x1c) = 0;
  *(undefined2 *)(in_ECX + 0x1e) = 0;
  return (int)in_ECX;
}
