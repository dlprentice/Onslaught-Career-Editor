/* address: 0x004a1c30 */
/* name: CMemoryManager__ReleaseMutexCallback */
/* signature: void __fastcall CMemoryManager__ReleaseMutexCallback(void * param_1) */


void __fastcall CMemoryManager__ReleaseMutexCallback(void *param_1)

{
  ReleaseMutex(*(HANDLE *)param_1);
  return;
}
