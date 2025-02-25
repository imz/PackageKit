/* pkg-list.h
 *
 * Copyright (c) 2012-2016 Daniel Nicoletti <dantti12@gmail.com>
 * Copyright (c) 2015-2022 Matthias Klumpp <matthias@tenstral.net>
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
#ifndef PKG_LIST_H
#define PKG_LIST_H

#include <apt-pkg/pkgcache.h>

#include <vector>

using std::vector;

/**
 * A designated action to perform on a package.
 */
enum class PkgAction
{
    NONE,
    INSTALL_AUTO,
    INSTALL_MANUAL
};

/**
 * Whether a package needs resolving its deps etc or
 * it has been marked for install and all deps resolved
 * (as a result of a recursive MarkInstall or DistUpgrade; i.e.,
 * it is a part of a ready solution and must not provoke the search
 * for a different solution by a recursive MarkInstall).
 */
enum class PkgSolved
{
    UNSOLVED,
    SOLVED
};

/**
 * Information about a package, mainly containing its VerIterator
 * and some information about the intended action on a package
 * extracted from a PackageKit package-ID.
 */
class PkgInfo
{
public:
    explicit PkgInfo(const pkgCache::VerIterator &verIter, PkgSolved s)
        : ver(verIter),
          action(PkgAction::NONE),
          solved(s) {};
    explicit PkgInfo(const pkgCache::VerIterator &verIter, PkgSolved s, PkgAction a)
        : ver(verIter),
          action(a),
          solved(s) {};
    pkgCache::VerIterator ver;
    PkgAction action;
    PkgSolved solved;
};

/**
 * This class is meant to show Operation Progress using PackageKit
 */
class PkgList : public vector<PkgInfo>
{
public:
    /**
     * Add a new package to the list
     * @param verIter The pkgCache::VerIterator assoicated with this package.
     * @param action An optional action that should be performed on this package in future.
     */
    void append(const pkgCache::VerIterator &verIter,
                PkgSolved solved,
                PkgAction action = PkgAction::NONE);

    void append(const PkgInfo &pi) { this->push_back(pi); };

    /**
     * Return if the given vector contain a package
     */
    bool contains(const pkgCache::PkgIterator &pkg);

    /**
     * Sort the package list
     */
    void sort();

    /**
     * Remove duplicated packages (it's recommended to sort() first)
     */
    void removeDuplicates();
};

#endif // PKG_LIST_H
