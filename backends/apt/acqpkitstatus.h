/* acqpkitstatus.h
 *
 * Copyright (c) 2009 Daniel Nicoletti <dantti12@gmail.com>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; see the file COPYING.  If not, write to
 * the Free Software Foundation, Inc., 59 Temple Place - Suite 330,
 * Boston, MA 02111-1307, USA.
 */

#ifndef ACQ_PKIT_STATUS_H
#define ACQ_PKIT_STATUS_H

#include <set>
#include <string>
#include <apt-pkg/acquire-item.h>
#include <pk-backend.h>

#include "pkg-list.h"

using std::set;
using std::string;

class AptJob;
class AcqPackageKitStatus : public pkgAcquireStatus
{
public:
    AcqPackageKitStatus(AptJob *apt);

    virtual bool MediaChange(string Media, string Drive) override;
    virtual void IMSHit(pkgAcquire::ItemDesc &Itm) override;
    virtual void Fetch(pkgAcquire::ItemDesc &Itm) override;
    virtual void Done(pkgAcquire::ItemDesc &Itm) override;
    virtual void Fail(pkgAcquire::ItemDesc &Itm) override;
    virtual void Start() override;
    virtual void Stop() override;

    bool Pulse(pkgAcquire *Owner) override;

private:
    void updateStatus(pkgAcquire::ItemDesc & Itm, int status);

    unsigned long m_lastPercent;
    double        m_lastCPS;

    AptJob       *m_apt;
    PkBackendJob *m_job;
};

class pkgAcqArchiveSane : public pkgAcqArchive
{
public:
    // This is insane the version is protected
    pkgCache::VerIterator version() { return Version; }
};

#endif
