/* address: 0x004a1c30 */
/* name: CMemoryManager__Unk_004a1c30 */
/* signature: void __fastcall CMemoryManager__Unk_004a1c30(void * param_1) */


void __fastcall CMemoryManager__Unk_004a1c30(void *param_1)

{
  ReleaseMutex(*(HANDLE *)param_1);
  return;
}
